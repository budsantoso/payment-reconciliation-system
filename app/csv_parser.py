import csv
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.models import GatewaySettlement, InternalTransaction

T = TypeVar('T', bound=BaseModel)


def _money(value: str) -> Decimal:
    cleaned = (value or '').replace(',', '').strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f'Invalid amount: {value}') from exc


def _parse_rows(content: str, model: type[T], amount_fields: set[str]) -> list[T]:
    reader = csv.DictReader(StringIO(content.strip()))
    if not reader.fieldnames:
        raise ValueError('CSV file has no header')

    rows: list[T] = []
    errors: list[str] = []

    for line_no, raw in enumerate(reader, start=2):
        normalized = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw.items() if k}
        for field in amount_fields:
            if field in normalized:
                normalized[field] = _money(normalized[field])

        try:
            rows.append(model(**normalized))
        except (ValidationError, ValueError) as exc:
            errors.append(f'line {line_no}: {exc}')

    if errors:
        raise ValueError('; '.join(errors))

    return rows


def parse_internal_transactions(content: str) -> list[InternalTransaction]:
    return _parse_rows(content, InternalTransaction, {'amount'})


def parse_gateway_settlements(content: str) -> list[GatewaySettlement]:
    return _parse_rows(content, GatewaySettlement, {'amount'})
