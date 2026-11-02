import io

from fastapi import APIRouter, HTTPException, UploadFile

from model.portfolio import PortfolioMovementDTO, PortfolioSnapshotDTO
from registry import registry

router = APIRouter()


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
):
    contents = await _read_file(file)
    values = registry.parser.parse_portfolio_snapshot_file(file.filename, contents)
    dtos = [PortfolioSnapshotDTO.from_value_to_dto(value) for value in values]
    return registry.storage.save_portfolio_snapshot(data=dtos)


@router.post("/movements")
async def upload_portfolio_movements(
    file: UploadFile,
):
    contents = await _read_file(file)
    values = registry.parser.parse_portfolio_movements_file(file.filename, contents)
    dtos = [PortfolioMovementDTO.from_value_to_dto(value) for value in values]
    return registry.storage.save_portfolio_movements(data=dtos)
