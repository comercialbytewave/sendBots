from __future__ import annotations

import argparse
from pathlib import Path

from sendbots.config import ConfigStore, database_path, logs_dir
from sendbots.logging_setup import setup_logging
from sendbots.sender import SenderService
from sendbots.storage import HistoryStore
from sendbots.watcher import scan_folder


def main(argv: list[str] | None = None) -> None:
    setup_logging()
    args = _parse_args(argv)
    if args.paths:
        print(f"Banco: {database_path()}")
        print(f"Logs: {logs_dir()}")
        return
    if args.scan_once:
        _scan_once()
        return
    _launch_gui()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SendBots - envio AlowChat")
    parser.add_argument("--scan-once", action="store_true", help="executa uma varredura usando a configuracao salva")
    parser.add_argument("--paths", action="store_true", help="exibe locais de banco e logs")
    return parser.parse_args(argv)


def _launch_gui() -> None:
    try:
        from sendbots.ui import SendBotsApp
    except ModuleNotFoundError as exc:
        if exc.name == "tkinter":
            raise SystemExit(
                "Tkinter nao esta instalado neste Python. No Windows empacotado ele sera incluido; "
                "em Linux instale o pacote python3-tk para abrir a interface."
            ) from exc
        raise

    app = SendBotsApp()
    app.mainloop()


def _scan_once() -> None:
    config = ConfigStore().load()
    errors = config.validate()
    if errors:
        raise SystemExit("\n".join(errors))

    history = HistoryStore()
    groups, invalid, skipped = scan_folder(Path(config.watched_folder))
    print(f"Grupos encontrados: {len(groups)}")
    print(f"Arquivos invalidos: {len(invalid)}")
    if skipped:
        print(f"Arquivos enviados que nao puderam ser movidos: {len(skipped)}")

    for path in invalid:
        detail = (
            "Nome fora do padrao esperado. Use "
            "Nfe[NumeroNota]_[WhatsApp]_[ChaveAcesso].pdf ou "
            "Boleto[NumeroBoleto]_[WhatsApp]_[CodigoBarras].pdf."
        )
        print(f"Arquivo invalido ignorado: {path}. {detail}")
        history.add("", [str(path)], "invalid", detail)

    service = SenderService(config, history)
    for group in groups:
        result = service.process_group(group)
        status = "OK" if result.success else "FALHA"
        detail = result.error or result.response_body
        print(
            f"{status} {group.whatsapp}: "
            f"notas={len(group.notes)} boletos={len(group.boletos)} "
            f"{detail[:500]}"
        )
