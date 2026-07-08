from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any


LOGGER = logging.getLogger(__name__)


class TrayController:
    def __init__(self, restore_callback: Callable[[], None], quit_callback: Callable[[], None]) -> None:
        self.restore_callback = restore_callback
        self.quit_callback = quit_callback
        self.icon: Any | None = None
        self.thread: threading.Thread | None = None
        self.started = False

    @property
    def is_running(self) -> bool:
        return self.started and self.icon is not None

    def start(self) -> bool:
        if self.is_running:
            return True

        try:
            import pystray
        except ModuleNotFoundError:
            LOGGER.warning("pystray nao instalado; bandeja do sistema indisponivel.")
            return False

        try:
            image = _create_icon_image()
        except RuntimeError as exc:
            LOGGER.warning(str(exc))
            return False

        menu = pystray.Menu(
            pystray.MenuItem("Abrir SendBots", self._on_restore, default=True),
            pystray.MenuItem("Sair", self._on_quit),
        )
        self.icon = pystray.Icon("SendBots", image, "SendBots", menu)
        self.thread = threading.Thread(target=self.icon.run, name="sendbots-tray", daemon=True)
        self.thread.start()
        self.started = True
        LOGGER.info("Icone da bandeja iniciado.")
        return True

    def stop(self) -> None:
        if self.icon:
            self.icon.stop()
            self.icon = None
        self.thread = None
        self.started = False

    def _on_restore(self, _icon: Any, _item: Any) -> None:
        self.restore_callback()

    def _on_quit(self, _icon: Any, _item: Any) -> None:
        self.quit_callback()


def _create_icon_image() -> Any:
    try:
        from PIL import Image, ImageDraw
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pillow nao instalado; nao foi possivel criar o icone da bandeja.") from exc

    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((6, 6, 58, 58), radius=12, fill=(22, 98, 181, 255))
    draw.rounded_rectangle((14, 18, 50, 46), radius=5, fill=(255, 255, 255, 255))
    draw.line((16, 20, 32, 34, 48, 20), fill=(22, 98, 181, 255), width=4)
    draw.line((18, 44, 46, 44), fill=(22, 98, 181, 255), width=4)
    return image
