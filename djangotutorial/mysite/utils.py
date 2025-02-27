import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import logging


def load_message(
    message: str,
) -> dict | str:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return message


def message_to_json(
    message: dict | str,
    default_to: Callable = repr,
) -> str:
    return json.dumps(
        message,
        ensure_ascii=False,
        default=default_to,
        sort_keys=True,
    )


def make_log(
    logger: "logging.Logger",
    message: dict | str,
    level: Literal["debug", "info", "warning", "error"] = "debug",
    **kwargs: object,
) -> None:
    methods = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "exception": logger.exception,
    }
    method = methods.get(level, logger.debug)

    method(
        msg=message_to_json(message),
        **kwargs,
    )
