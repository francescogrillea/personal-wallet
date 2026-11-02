import io

from fastapi import APIRouter, HTTPException, UploadFile

from model.transaction import TransactionDTO
from registry import registry

router = APIRouter()


@router.post("/movements")
async def upload_liquidity_movements(
    file: UploadFile,
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")

    transactions = registry.parser.parse_liquidity_movements_file(file.filename, io.BytesIO(contents))
    dtos = [TransactionDTO.from_value_to_dto(transaction) for transaction in transactions]
    return registry.storage.save_liquidity_movements(data=dtos)
