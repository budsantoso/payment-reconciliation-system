from collections import Counter, defaultdict
from decimal import Decimal

from app.models import (
    DiscrepancyItem,
    DiscrepancyType,
    GatewaySettlement,
    InternalTransaction,
    ReconciliationReport,
    ReconciliationSummary,
)

PAID_STATUSES = {'PAID', 'SUCCESS', 'SETTLED', 'CAPTURED'}


def _is_success(status: str) -> bool:
    return status.upper() in PAID_STATUSES


def reconcile(
    internal_transactions: list[InternalTransaction],
    gateway_settlements: list[GatewaySettlement],
) -> ReconciliationReport:
    gateway_by_ref: dict[str, list[GatewaySettlement]] = defaultdict(list)
    for settlement in gateway_settlements:
        gateway_by_ref[settlement.payment_reference].append(settlement)

    discrepancies: list[DiscrepancyItem] = []
    matched_count = 0
    seen_gateway_refs: set[str] = set()

    for transaction in internal_transactions:
        ref = transaction.payment_reference
        if not ref:
            discrepancies.append(
                DiscrepancyItem(
                    invoice_number=transaction.invoice_number,
                    internal_amount=transaction.amount,
                    internal_status=transaction.status,
                    discrepancy_type=DiscrepancyType.MISSING_IN_GATEWAY,
                    details='Internal transaction has no payment reference',
                )
            )
            continue

        settlements = gateway_by_ref.get(ref, [])
        if not settlements:
            discrepancies.append(
                DiscrepancyItem(
                    invoice_number=transaction.invoice_number,
                    payment_reference=ref,
                    internal_amount=transaction.amount,
                    internal_status=transaction.status,
                    discrepancy_type=DiscrepancyType.MISSING_IN_GATEWAY,
                    details='Payment reference not found in gateway settlement report',
                )
            )
            continue

        if len(settlements) > 1:
            discrepancies.append(
                DiscrepancyItem(
                    invoice_number=transaction.invoice_number,
                    payment_reference=ref,
                    internal_amount=transaction.amount,
                    gateway_amount=sum((s.amount for s in settlements), Decimal('0')),
                    internal_status=transaction.status,
                    gateway_status=','.join(s.status for s in settlements),
                    discrepancy_type=DiscrepancyType.DUPLICATE_IN_GATEWAY,
                    details='Multiple gateway settlement rows found for one payment reference',
                )
            )
            seen_gateway_refs.add(ref)
            continue

        settlement = settlements[0]
        seen_gateway_refs.add(ref)

        if transaction.amount != settlement.amount:
            discrepancies.append(
                DiscrepancyItem(
                    invoice_number=transaction.invoice_number,
                    payment_reference=ref,
                    internal_amount=transaction.amount,
                    gateway_amount=settlement.amount,
                    internal_status=transaction.status,
                    gateway_status=settlement.status,
                    discrepancy_type=DiscrepancyType.AMOUNT_MISMATCH,
                    details='Internal amount differs from gateway amount',
                )
            )
            continue

        if _is_success(transaction.status) != _is_success(settlement.status):
            discrepancies.append(
                DiscrepancyItem(
                    invoice_number=transaction.invoice_number,
                    payment_reference=ref,
                    internal_amount=transaction.amount,
                    gateway_amount=settlement.amount,
                    internal_status=transaction.status,
                    gateway_status=settlement.status,
                    discrepancy_type=DiscrepancyType.STATUS_MISMATCH,
                    details='Internal payment status differs from gateway settlement status',
                )
            )
            continue

        matched_count += 1

    for settlement in gateway_settlements:
        if settlement.payment_reference not in seen_gateway_refs:
            discrepancies.append(
                DiscrepancyItem(
                    payment_reference=settlement.payment_reference,
                    gateway_amount=settlement.amount,
                    gateway_status=settlement.status,
                    discrepancy_type=DiscrepancyType.MISSING_IN_INTERNAL,
                    details='Gateway settlement row has no matching internal transaction',
                )
            )

    internal_total = sum((item.amount for item in internal_transactions), Decimal('0'))
    gateway_total = sum((item.amount for item in gateway_settlements), Decimal('0'))
    breakdown = Counter(item.discrepancy_type.value for item in discrepancies)
    breakdown[DiscrepancyType.MATCHED.value] = matched_count

    return ReconciliationReport(
        summary=ReconciliationSummary(
            total_internal_records=len(internal_transactions),
            total_gateway_records=len(gateway_settlements),
            matched_count=matched_count,
            discrepancy_count=len(discrepancies),
            total_internal_amount=internal_total,
            total_gateway_amount=gateway_total,
            amount_difference=internal_total - gateway_total,
            breakdown=dict(sorted(breakdown.items())),
        ),
        discrepancies=discrepancies,
    )
