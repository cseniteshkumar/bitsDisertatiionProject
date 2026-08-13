import aiofiles
import asyncio
import importlib
import json
import subprocess
import sys
import traceback
from typing import Any
from colorama import Fore, Style, init
import os
from enum import Enum

_SUPPORTED_PROVIDERS = {"ollama"}

NO_SUPPORT_TEMPERATURE_MODELS = []
SUPPORT_REASONING_EFFORT_MODELS = []

class ReasoningEfforts(Enum):
    High = "high"
    Medium = "medium"
    Low = "low"


class ChatLogger:
    """Helper utility to log all chat requests and their corresponding responses
    plus the stack trace leading to the call.
    """

    def __init__(self, fname: str):
        self.fname = fname
        self._lock = asyncio.Lock()

    async def log_request(self, messages, response):
        async with self._lock:
            async with aiofiles.open(self.fname, mode="a", encoding="utf-8") as handle:
                await handle.write(json.dumps({
                    "messages": messages,
                    "response": response,
                    "stacktrace": traceback.format_exc()
                }) + "\n")

class GenericLLMProvider:

    def __init__(self, llm, chat_log: str | None = None,  verbose: bool = True):
        self.llm = llm
        self.chat_logger = ChatLogger(chat_log) if chat_log else None
        self.verbose = verbose
        self.last_usage_metadata: dict[str, Any] | None = None
        self.last_response_metadata: dict[str, Any] = {}

    def _reset_last_response_metadata(self) -> None:
        self.last_usage_metadata = None
        self.last_response_metadata = {}

    def _capture_response_metadata(self, message: Any) -> None:
        usage_metadata = getattr(message, "usage_metadata", None)
        if usage_metadata:
            if hasattr(usage_metadata, "model_dump"):
                usage_metadata = usage_metadata.model_dump()
            self.last_usage_metadata = dict(usage_metadata)

        response_metadata = getattr(message, "response_metadata", None)
        if response_metadata:
            if hasattr(response_metadata, "model_dump"):
                response_metadata = response_metadata.model_dump()
            self.last_response_metadata = {
                **self.last_response_metadata,
                **dict(response_metadata),
            }

    @classmethod
    def from_provider(cls, provider: str, chat_log: str | None = None, verbose: bool=True, **kwargs: Any):
        if provider != "ollama":
            raise ValueError(
                f"Unsupported provider '{provider}'. This project is configured for Ollama only. "
                "Use model strings like 'ollama:llama3.1'."
            )

        _check_pkg("langchain_community")
        _check_pkg("langchain_ollama")
        from langchain_ollama import ChatOllama

        base_url = kwargs.pop("base_url", None) or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        llm = ChatOllama(base_url=base_url, **kwargs)
        return cls(llm, chat_log, verbose=verbose)


    async def get_chat_response(self, messages, stream, websocket=None, **kwargs):
        self._reset_last_response_metadata()
        if not stream:
            # Getting output from the model chain using ainvoke for asynchronous invoking
            output = await self.llm.ainvoke(messages, **kwargs)
            self._capture_response_metadata(output)

            res = output.content

        else:
            res = await self.stream_response(messages, websocket, **kwargs)

        if self.chat_logger:
            await self.chat_logger.log_request(messages, res)

        return res

    async def stream_response(self, messages, websocket=None, **kwargs):
        self._reset_last_response_metadata()
        paragraph = ""
        response = ""

        # Streaming the response using the chain astream method from langchain
        async for chunk in self.llm.astream(messages, **kwargs):
            self._capture_response_metadata(chunk)
            content = chunk.content
            if not content:
                continue
            response += content
            paragraph += content
            if "\n" in paragraph:
                await self._send_output(paragraph, websocket)
                paragraph = ""

        if paragraph:
            await self._send_output(paragraph, websocket)

        return response

    async def _send_output(self, content, websocket=None):
        if websocket is not None:
            await websocket.send_json({"type": "report", "output": content})
        elif self.verbose:
            print(f"{Fore.GREEN}{content}{Style.RESET_ALL}", flush=True)


def _check_pkg(pkg: str) -> None:
    if not importlib.util.find_spec(pkg):
        pkg_kebab = pkg.replace("_", "-")
        # Import colorama and initialize it
        init(autoreset=True)

        try:
            print(f"{Fore.YELLOW}Installing {pkg_kebab}...{Style.RESET_ALL}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", pkg_kebab])
            print(f"{Fore.GREEN}Successfully installed {pkg_kebab}{Style.RESET_ALL}")

            # Try importing again after install
            importlib.import_module(pkg)

        except subprocess.CalledProcessError:
            raise ImportError(
                Fore.RED + f"Failed to install {pkg_kebab}. Please install manually with "
                f"`pip install -U {pkg_kebab}`"
            )
