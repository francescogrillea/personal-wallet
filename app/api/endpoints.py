from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.v1.router import router as v1_router

router = APIRouter()
router.include_router(v1_router)


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@router.get("/help")
def help() -> JSONResponse:
    return JSONResponse({
        "description": "Personal Wallet is a REST API for parsing and managing personal bank transaction and portfolio exports.",
        "endpoints": {
            "GET /health": "Returns the service health status.",
            "GET /help": "Returns this help message.",
            "POST /api/v1/liquidity/movements": "Upload a bank liquidity movements file. Requires multipart form fields file, bank_id, storage_id, and storage_config.",
            "POST /api/v1/portfolio/snapshot": "Upload a portfolio snapshot file. Requires multipart form fields file, bank_id, storage_id, and storage_config.",
            "POST /api/v1/portfolio/movements": "Upload a portfolio movements file. Requires multipart form fields file, bank_id, storage_id, and storage_config.",
        }
    })


