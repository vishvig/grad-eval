from fastapi import APIRouter
from ..apis.mcq import router_mcq
from ..apis.auth import router_auth
from ..apis.coding_task import router_coding_task
from ..apis.chat import router_chat

router = APIRouter()
router.include_router(router_mcq)
router.include_router(router_auth)
router.include_router(router_coding_task)
router.include_router(router_chat)
