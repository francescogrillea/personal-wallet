import io

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from model.transaction import TransactionDTO
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


@router.post("/upload")
async def upload(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    transactions = registry.parsing_service.parse(file.filename, io.BytesIO(contents))
    dtos = [TransactionDTO.from_transaction(t) for t in transactions]
    result = registry.storage_service.save(dtos)

    return result
