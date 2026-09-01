import io
import json

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from model.transaction import TransactionDTO
from model.portfolio import PortfolioSnapshotDTO
from registry import registry

router = APIRouter()


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@router.get("/help")
def help() -> JSONResponse:
    return JSONResponse({
        "description": "Personal Wallet is a REST API for parsing and managing personal bank transaction exports. It accepts standard .xlsx bank movement files and returns structured transaction records with value date, accounting date, amount, and description.",
        "endpoints": {
            "GET /health": "Returns the service health status.",
            "GET /help": "Returns this help message.",
            "POST /upload": "Upload a standard .xlsx movements file. Returns a list of parsed transactions.",
        }
    })


@router.post("/api/v1/transactions")
async def upload_transactions_file(file: UploadFile, bank_id: str = Form(...),
                                    storage_id: str = Form(...), storage_config: str = Form(...)):

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    storage_config = json.loads(storage_config)
    parser = registry.parsing_service_registry.get(bank_id)
    storage = registry.storage_service_registry.get(storage_id)(**storage_config)
    
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser found for bank_id '{bank_id}'.")
    if not storage:
        raise HTTPException(status_code=400, detail=f"No storage found for storage_id '{storage_id}'.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    transactions = parser.parse_transactions(file.filename, io.BytesIO(contents))
    dtos = [TransactionDTO.from_value_to_dto(t) for t in transactions]
    result = storage.save_transactions(data=dtos, **storage_config)

    return result


@router.post("/api/v1/portfolio")
async def upload_portfolio_file(file: UploadFile, bank_id: str = Form(...),
                                storage_id: str = Form(...), storage_config: str = Form(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    parser = registry.parsing_service_registry.get(bank_id)
    storage = registry.storage_service_registry.get(storage_id)(**storage_config)
    storage_config = json.loads(storage_config)
    
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser found for bank_id '{bank_id}'.")
    if not storage:
        raise HTTPException(status_code=400, detail=f"No storage found for storage_id '{storage_id}'.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    values = parser.parse_investments(file.filename, io.BytesIO(contents))
    dtos = [PortfolioSnapshotDTO.from_value_to_dto(v) for v in values]
    result = storage.save_portfolio(data=dtos, **storage_config)

    return result

