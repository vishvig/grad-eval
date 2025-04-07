from fastapi import APIRouter
from ..apis.mcq import router_mcq
from ..apis.auth import router_auth

router = APIRouter()
router.include_router(router_mcq)
router.include_router(router_auth)
