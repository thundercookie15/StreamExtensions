from . import engine as engine


def init(driverName: str | None = ..., debug: bool = ...) -> engine.Engine: ...


def speak(text: str) -> None: ...
