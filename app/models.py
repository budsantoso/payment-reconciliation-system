from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DiscrepancyType(str, Enum):
    MATCHED = "MATCHED"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    STATUS_MISMATCH = "STATUS_MISMATCH"
    MISSING_IN_GATEWAY = "MISSING_IN_GATEWAY"
    MISSING_IN_INTERNAL = "MISSING_IN_INTERNAL"
    DUPLICATE_IN_GATEWAY = "DUPLICATE_IN_GATEWAY"


class InternalTransaction(BaseModel):
    invoice_number: str
    amount: Decimal
    status: str
    payment_reference: Optional[str] = None


class GatewaySettlement(BaseModel):
    payment_reference: str
    amount: Decimal
    status: str
    settled_at: Optional[str] = None


class DiscrepancyItem(BaseModel):
    invoice_number: Optional[str] = None
    payment_reference: Optional[str] = None
    internal_amount: Optional[Decimal] = None
    gateway_amount: Optional[Decimal] = None
    internal_status: Optional[str] = None
    gateway_status: Optional[str] = None
    discrepancy_type: DiscrepancyType
    details: str


class ReconciliationSummary(BaseModel):
    total_internal_records: int
    total_gateway_records: int
    matched_count: int
    discrepancy_count: int
    total_internal_amount: Decimal
    total_gateway_amount: Decimal
    amount_difference: Decimal
    breakdown: dict[str, int]


class ReconciliationReport(BaseModel):
    summary: ReconciliationSummary
    discrepancies: list[DiscrepancyItem]
