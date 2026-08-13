"""Tool-enabled LLM utilities for the backend package.

This module provides `create_chat_completion_with_tools` and helper
tool builders. It was copied from the previous canonical implementation
so modules can import these helpers from `backend.utils.tools` after
the consolidation.
"""
import asyncio
import logging
from typing import Any, Dict, List, Tuple, Callable, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool

from .costs import calculate_llm_cost
from .llm import create_chat_completion

logger = logging.getLogger(__name__)


def _track_response_cost(
    *,
    llm_provider: str | None,
    model: str | None,
    input_payload: Any,
    response_message: Any,
    request_options: Dict[str, Any],
    cost_callback: Callable | None,
) -> None:
    if not cost_callback:
        return

    response_content = getattr(response_message, "content", "") or ""
    llm_costs = calculate_llm_cost(
        llm_provider=llm_provider,
        model=model,
        input_content=str(input_payload),
        output_content=str(response_content),
        response_metadata=getattr(response_message, "response_metadata", None),
        usage_metadata=getattr(response_message, "usage_metadata", None),
        request_options=request_options,
    )
    cost_callback(llm_costs)


async def create_chat_completion_with_tools(
    messages: List[Dict[str, str]],
    tools: List[Callable],
    model: str | None = None,
    temperature: float | None = 0.4,
    max_tokens: int | None = 4000,
    llm_provider: str | None = None,
    llm_kwargs: Dict[str, Any] | None = None,
    cost_callback: Callable = None,
    websocket: Any | None = None,
    **kwargs
) -> Tuple[str, List[Dict[str, Any]]]:
    try:
        from backend.llm_provider.generic.base import GenericLLMProvider

        provider_kwargs = {
            'model': model,
            **(llm_kwargs or {})
        }

        llm_provider_instance = GenericLLMProvider.from_provider(
            llm_provider,
            **provider_kwargs
        )

        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        llm_with_tools = llm_provider_instance.llm.bind_tools(tools)

        logger.info(f"Invoking LLM with {len(tools)} available tools")

        from langchain_core.messages import ToolMessage

        response = await llm_with_tools.ainvoke(lc_messages)
        _track_response_cost(
            llm_provider=llm_provider,
            model=model,
            input_payload=lc_messages,
            response_message=response,
            request_options=provider_kwargs,
            cost_callback=cost_callback,
        )

        tool_calls_metadata = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"LLM made {len(response.tool_calls)} tool calls")
            lc_messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id', '')

                logger.info(f"Tool called: {tool_name}")
                if tool_args:
                    args_str = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
                    logger.debug(f"Tool arguments: {args_str}")

                tool_result = "Tool execution failed"
                for tool in tools:
                    if getattr(tool, 'name', None) == tool_name or getattr(tool, '__name__', None) == tool_name:
                        try:
                            if hasattr(tool, 'ainvoke'):
                                tool_result = await tool.ainvoke(tool_args)
                            elif hasattr(tool, 'invoke'):
                                tool_result = tool.invoke(tool_args)
                            else:
                                tool_result = await tool(**tool_args) if asyncio.iscoroutinefunction(tool) else tool(**tool_args)
                            break
                        except Exception as e:
                            error_msg = str(e)
                            logger.error(f"Error executing tool '{tool_name}': {error_msg}", exc_info=True)
                            if "timeout" in error_msg.lower():
                                tool_result = f"Tool '{tool_name}' timed out. The operation took too long to complete."
                            else:
                                tool_result = f"Tool '{tool_name}' encountered an error: {error_msg}."

                tool_message = ToolMessage(content=str(tool_result), tool_call_id=tool_id)
                lc_messages.append(tool_message)

                tool_calls_metadata.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "call_id": tool_id,
                    "result": str(tool_result)[:200] + "..." if len(str(tool_result)) > 200 else str(tool_result)
                })

            logger.info("Getting final response from LLM after tool execution")
            final_response = await llm_with_tools.ainvoke(lc_messages)

            _track_response_cost(
                llm_provider=llm_provider,
                model=model,
                input_payload=lc_messages,
                response_message=final_response,
                request_options=provider_kwargs,
                cost_callback=cost_callback,
            )

            return final_response.content, tool_calls_metadata
        else:
            return response.content, []

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in tool-enabled chat completion: {error_msg}", exc_info=True)
        logger.info("Falling back to simple chat completion without tools")

        response = await create_chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            llm_provider=llm_provider,
            llm_kwargs=llm_kwargs,
            cost_callback=cost_callback,
            websocket=websocket,
            **kwargs
        )
        return response, []


def create_search_tool(search_function: Callable[[str], Dict]) -> Callable:
    @tool
    def search_tool(query: str) -> str:
        try:
            results = search_function(query)
            if results and 'results' in results:
                search_content = f"Search results for '{query}':\n\n"
                for result in results['results'][:5]:
                    search_content += f"Title: {result.get('title', '')}\n"
                    search_content += f"Content: {result.get('content', '')[:300]}...\n"
                    search_content += f"URL: {result.get('url', '')}\n\n"
                return search_content
            else:
                return f"No search results found for: {query}"
        except Exception as e:
            logger.error(f"Search tool error: {e}", exc_info=True)
            return f"Search encountered an error: {e}"

    return search_tool


def create_custom_tool(
    name: str,
    description: str,
    function: Callable,
    parameter_schema: Optional[Dict] = None
) -> Callable:
    @tool
    def custom_tool(*args, **kwargs) -> str:
        try:
            result = function(*args, **kwargs)
            return str(result) if result is not None else "Tool executed successfully"
        except Exception as e:
            logger.error(f"Custom tool '{name}' error: {e}", exc_info=True)
            return f"Tool '{name}' encountered an error: {e}"

    custom_tool.name = name
    custom_tool.description = description

    return custom_tool


def get_available_providers_with_tools() -> List[str]:
    return ["ollama"]


def supports_tools(provider: str) -> bool:
    return provider in get_available_providers_with_tools()
