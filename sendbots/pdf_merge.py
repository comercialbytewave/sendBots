from __future__ import annotations

import uuid
from pathlib import Path

from sendbots.config import user_data_dir
from sendbots.models import FileGroup


class PdfMergeError(RuntimeError):
    """Raised when the note and boleto cannot be merged."""


def merge_group_pdfs(group: FileGroup) -> Path:
    paths = [item.path for item in group.files]
    if len(paths) < 2:
        raise PdfMergeError("E necessario ter pelo menos dois PDFs para juntar.")

    return merge_pdfs(paths, f"Nota_Boleto_{group.whatsapp}_{uuid.uuid4().hex}.pdf")


def merge_pdfs(paths: list[Path], output_name: str) -> Path:
    try:
        from pypdf import PdfWriter
    except ModuleNotFoundError as exc:
        raise PdfMergeError(
            "Dependencia pypdf nao instalada no Python que abriu o app. "
            "No Linux, rode pela pasta do projeto com: ./scripts/run_local_linux.sh. "
            "Se estiver usando o executavel instalado, gere novamente com: ./scripts/build_linux.sh && ./scripts/install_linux.sh."
        ) from exc

    temp_dir = user_data_dir() / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_path = temp_dir / output_name

    writer = PdfWriter()
    try:
        for path in paths:
            writer.append(str(path))
        with output_path.open("wb") as fh:
            writer.write(fh)
    except Exception as exc:  # noqa: BLE001 - converted to user-facing error.
        output_path.unlink(missing_ok=True)
        raise PdfMergeError(f"Falha ao juntar PDFs: {exc}") from exc
    finally:
        close = getattr(writer, "close", None)
        if close:
            close()

    return output_path
