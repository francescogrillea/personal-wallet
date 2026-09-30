import io
import json

from fastapi import APIRouter, Form, HTTPException, UploadFile

from model.transaction import TransactionDTO
from registry import registry

router = APIRouter()


@router.post("/movements")
async def upload_liquidity_movements(
    file: UploadFile,
    bank_id: str = Form(...),
    storage_id: str = Form(...),
    storage_config: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    storage_config = json.loads(storage_config)
    parser = registry.parsing_service_registry.get(bank_id)
    storage_factory = registry.storage_service_registry.get(storage_id)
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser found for bank_id '{bank_id}'.")
    if not storage_factory:
        raise HTTPException(status_code=400, detail=f"No storage found for storage_id '{storage_id}'.")

    storage = storage_factory(**storage_config)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    transactions = parser.parse_liquidity_movements_file(file.filename, io.BytesIO(contents))
    dtos = [TransactionDTO.from_value_to_dto(transaction) for transaction in transactions]
    return storage.save_liquidity_movements(data=dtos, **storage_config)
