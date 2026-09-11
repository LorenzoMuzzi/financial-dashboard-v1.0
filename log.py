from datetime import datetime
from config import DEFAULT_DATE_FORMAT

fmt = DEFAULT_DATE_FORMAT + " %H:%M:%S"

info_API =  "To get your FRED API key, please visit: https://fred.stlouisfed.org/docs/api/api_key.html.\nYou can use the button below to directly open the webpage."

def _timestamp() -> None:
    return datetime.now().strftime(fmt)


def _format_message(message, level="INFO") -> str:
    return f"[{_timestamp()}] [{level}] {message}"


def log_info(message: str, target=None) -> None: # target None invia al terminale
    log(message, target=target)


def log_success(message: str, target=None) -> None:
    log(message, level="SUCCESS", target=target)


def log_warning(message: str, target=None) -> None:
    log(message, level="WARNING", target=target)


def log_error(message: str, target=None) -> None:
    log(message, level="ERROR", target=target)


def log(message: str, level="INFO", target=None) -> None:
    formatted = _format_message(message, level)

    if target is None:
        print(formatted)
    else:
        send_to_target(formatted, target)


def send_to_target(message: str, target) -> None:
    """
    if target is:
    - a function --> it calls the function with the message as attribute
    - a tkinter Label --> it changes the text of the Label in the value of message
    - a tkinter Text --> it adds the value of message at the end of a tkinter Text
    """

    if callable(target):
        target(message)

    elif hasattr(target, "config"):
        target.config(text=message)

    elif hasattr(target, "insert"):
        target.insert("end", message + "\n")
        target.see("end")

    else:
        print(message)