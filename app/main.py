from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.csv_parser import parse_gateway_settlements, parse_internal_transactions
from app.reconciliation import reconcile
from app.reporting import report_to_csv

settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.PROJECT_NAME}


async def _read_upload(file: UploadFile) -> str:
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='File too large')
    return content.decode('utf-8-sig')


@app.post('/reconcile')
async def reconcile_files(
    internal_file: UploadFile = File(...),
    gateway_file: UploadFile = File(...),
):
    try:
        internal = parse_internal_transactions(await _read_upload(internal_file))
        gateway = parse_gateway_settlements(await _read_upload(gateway_file))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return reconcile(internal, gateway)


@app.post('/reconcile.csv', response_class=PlainTextResponse)
async def reconcile_files_csv(
    internal_file: UploadFile = File(...),
    gateway_file: UploadFile = File(...),
):
    report = await reconcile_files(internal_file, gateway_file)
    return report_to_csv(report)
