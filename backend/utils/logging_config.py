try:
    from gpt_researcher.utils.logging_config import *  # noqa: F401,F403
except Exception:  # pragma: no cover
    def get_json_handler(*args, **kwargs):
        raise ImportError("backend.utils.logging_config is unavailable; ensure gpt_researcher is importable")
