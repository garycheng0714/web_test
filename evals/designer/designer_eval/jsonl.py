"""Read and write the eval's line-delimited model files."""

from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel


def read_rows[RowT: BaseModel](path: Path, model: type[RowT]) -> list[RowT]:
    """One row per non-blank line, validated by `model`."""
    return [
        model.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_rows(path: Path, rows: Iterable[BaseModel]) -> None:
    """One row per line, `null` fields included: a row keeps its explicit `human_mode: null`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(row.model_dump_json(exclude_none=False) + "\n" for row in rows), encoding="utf-8"
    )
