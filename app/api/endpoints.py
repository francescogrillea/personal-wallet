from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from api.v1.router import router as v1_router

router = APIRouter()
router.include_router(v1_router)


@router.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(Path(__file__).resolve().parents[1] / "static" / "index.html")


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
            "POST /api/v1/liquidity/movements": "Upload a bank liquidity movements file. Requires only the multipart form field file.",
            "POST /api/v1/portfolio/snapshot": "Upload a portfolio snapshot file. Requires only the multipart form field file.",
            "POST /api/v1/portfolio/movements": "Upload a portfolio movements file. Requires only the multipart form field file.",
        }
    })


