from fastapi import APIRouter

from api.v1 import liquidity, portfolio

router = APIRouter(prefix="/api/v1")
router.include_router(liquidity.router, prefix="/liquidity", tags=["liquidity"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
