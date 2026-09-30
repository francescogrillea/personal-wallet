import io
import json

from fastapi import APIRouter, Form, HTTPException, UploadFile

from model.portfolio import PortfolioMovementDTO, PortfolioSnapshotDTO
from registry import registry

router = APIRouter()


def _get_parser_and_storage(bank_id: str, storage_id: str, storage_config: str):
    config = json.loads(storage_config)
    parser = registry.parsing_service_registry.get(bank_id)
    storage_factory = registry.storage_service_registry.get(storage_id)
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser found for bank_id '{bank_id}'.")
    if not storage_factory:
        raise HTTPException(status_code=400, detail=f"No storage found for storage_id '{storage_id}'.")
    return parser, storage_factory(**config), config


async def _read_file(file: UploadFile) -> io.BytesIO:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty.")
    return io.BytesIO(contents)


@router.post("/snapshot")
async def upload_portfolio_snapshot(
    file: UploadFile,
    bank_id: str = Form(...),
    storage_id: str = Form(...),
    storage_config: str = Form(...),
):
    parser, storage, config = _get_parser_and_storage(bank_id, storage_id, storage_config)
    contents = await _read_file(file)
    values = parser.parse_portfolio_snapshot_file(file.filename, contents)
    dtos = [PortfolioSnapshotDTO.from_value_to_dto(value) for value in values]
    return storage.save_portfolio_snapshot(data=dtos, **config)


@router.post("/movements")
async def upload_portfolio_movements(
    file: UploadFile,
    bank_id: str = Form(...),
    storage_id: str = Form(...),
    storage_config: str = Form(...),
):
    parser, storage, config = _get_parser_and_storage(bank_id, storage_id, storage_config)
    contents = await _read_file(file)
    values = parser.parse_portfolio_movements_file(file.filename, contents)
    dtos = [PortfolioMovementDTO.from_value_to_dto(value) for value in values]
    return storage.save_portfolio_movements(data=dtos, **config)
