import io
import logging

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from auth import CurrentUser
from model.transaction import TransactionDTO
from registry import registry

logger = logging.getLogger(__name__)

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
            "GET /me": "Returns the authenticated Google account. Requires a Bearer ID token.",
            "POST /upload": "Upload a standard .xlsx movements file. Returns a list of parsed transactions. Requires a Bearer ID token.",
        },
        "authentication": "Every endpoint except /health and /help requires an 'Authorization: Bearer <Google ID token>' header.",
    })


@router.get("/me")
def me(user: CurrentUser) -> JSONResponse:
    return JSONResponse({"sub": user.sub, "email": user.email, "name": user.name})


@router.post("/upload")
async def upload(user: CurrentUser, file: UploadFile, bank_id: str = Form(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    parser = registry.parsing_service_registry.get(bank_id)
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser found for bank_id '{bank_id}'.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    transactions = parser.parse(file.filename, io.BytesIO(contents))
    dtos = [TransactionDTO.from_transaction(t) for t in transactions]
    result = registry.storage_service.save(dtos)
    logger.info("Saved %s transactions from '%s' for %s (%s).", result.items_saved, file.filename, user.email, user.sub)

    return result
