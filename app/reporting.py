import csv
from io import StringIO

from app.models import ReconciliationReport


def report_to_csv(report: ReconciliationReport) -> str:
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            'invoice_number',
            'payment_reference',
            'internal_amount',
            'gateway_amount',
            'internal_status',
            'gateway_status',
            'discrepancy_type',
            'details',
        ],
    )
    writer.writeheader()
    for item in report.discrepancies:
        writer.writerow(item.model_dump(mode='json'))
    return output.getvalue()
