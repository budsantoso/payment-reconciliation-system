from decimal import Decimal

from app.csv_parser import parse_gateway_settlements, parse_internal_transactions
from app.models import DiscrepancyType
from app.reconciliation import reconcile


def test_reconcile_all_match():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\nINV-001,100000,PAID,TRX-001\n")
    gateway = parse_gateway_settlements("payment_reference,amount,status,settled_at\nTRX-001,100000,SUCCESS,2026-10-01\n")
    report = reconcile(internal, gateway)
    assert report.summary.matched_count == 1
    assert report.summary.discrepancy_count == 0


def test_reconcile_amount_mismatch():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\nINV-001,100000,PAID,TRX-001\n")
    gateway = parse_gateway_settlements("payment_reference,amount,status,settled_at\nTRX-001,90000,SUCCESS,2026-10-01\n")
    report = reconcile(internal, gateway)
    assert report.summary.discrepancy_count == 1
    assert report.discrepancies[0].discrepancy_type == DiscrepancyType.AMOUNT_MISMATCH


def test_reconcile_missing_in_gateway():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\nINV-001,100000,PAID,TRX-001\n")
    gateway = parse_gateway_settlements("payment_reference,amount,status,settled_at\n")
    report = reconcile(internal, gateway)
    assert report.discrepancies[0].discrepancy_type == DiscrepancyType.MISSING_IN_GATEWAY


def test_reconcile_missing_in_internal():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\n")
    gateway = parse_gateway_settlements("payment_reference,amount,status,settled_at\nTRX-001,100000,SUCCESS,2026-10-01\n")
    report = reconcile(internal, gateway)
    assert report.discrepancies[0].discrepancy_type == DiscrepancyType.MISSING_IN_INTERNAL


def test_reconcile_duplicate_in_gateway():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\nINV-001,100000,PAID,TRX-001\n")
    gateway = parse_gateway_settlements(
        "payment_reference,amount,status,settled_at\nTRX-001,100000,SUCCESS,2026-10-01\nTRX-001,100000,SUCCESS,2026-10-01\n"
    )
    report = reconcile(internal, gateway)
    assert report.discrepancies[0].discrepancy_type == DiscrepancyType.DUPLICATE_IN_GATEWAY


def test_reconcile_status_mismatch():
    internal = parse_internal_transactions("invoice_number,amount,status,payment_reference\nINV-001,100000,PAID,TRX-001\n")
    gateway = parse_gateway_settlements("payment_reference,amount,status,settled_at\nTRX-001,100000,FAILED,2026-10-01\n")
    report = reconcile(internal, gateway)
    assert report.discrepancies[0].discrepancy_type == DiscrepancyType.STATUS_MISMATCH
