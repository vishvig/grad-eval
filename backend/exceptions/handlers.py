from fastapi import Request
from fastapi.responses import JSONResponse
from .mcq import MCQException, NoQuestionsAvailableError
from constants.constants import ResponseStates
from utils.logger_utility import logger


async def mcq_exception_handler(request: Request, exc: MCQException):
    """
    Handles all MCQ related exceptions and returns appropriate responses
    """
    if isinstance(exc, NoQuestionsAvailableError):
        logger.warning(f"No questions available: {str(exc)}")
        status = ResponseStates.WARNING
    else:
        logger.error(f"MCQ error occurred: {str(exc)}")
        status = ResponseStates.FAILED

    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "status": status,
            "message": str(exc),
            "body": None
        }
    ) 