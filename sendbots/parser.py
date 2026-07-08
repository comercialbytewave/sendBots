from __future__ import annotations

import re
from pathlib import Path

from sendbots.models import ParsedFile


NOTE_RE = re.compile(r"^Nfe(?P<document_id>[^_]+)_(?P<whatsapp>\d+)_(?P<reference>[^_]+)\.pdf$", re.IGNORECASE)
BOLETO_RE = re.compile(r"^Boleto(?P<document_id>[^_]+)_(?P<whatsapp>\d+)_(?P<reference>[^_]+)\.pdf$", re.IGNORECASE)
ENV_SUFFIX_RE = re.compile(r"_ENV(?:_\d+)?$", re.IGNORECASE)


def is_pdf(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def is_marked_sent(path: Path) -> bool:
    return bool(ENV_SUFFIX_RE.search(path.stem))


def parse_file(path: Path) -> ParsedFile | None:
    if not is_pdf(path) or is_marked_sent(path):
        return None
    name = path.name
    for kind, pattern in (("note", NOTE_RE), ("boleto", BOLETO_RE)):
        match = pattern.match(name)
        if match:
            return ParsedFile(
                path=path,
                kind=kind,
                document_id=match.group("document_id"),
                whatsapp=match.group("whatsapp"),
                reference=match.group("reference"),
            )
    return None
