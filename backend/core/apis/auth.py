from fastapi import APIRouter, HTTPException
from constants import constants
from ..handlers.auth import AuthHandler
from ..handlers.captcha import CaptchaHandler
from ..schemas.requests import auth as req_auth
from ..schemas.responses import auth as res_auth
from utils.logger_utility import logger

router_auth = APIRouter(prefix="/auth")


@router_auth.post("/verify",
                 response_model=res_auth.AuthResponse)
async def verify_auth(request: req_auth.GitlabAuthRequest):
    """Verify user authentication and captcha"""
    try:
        logger.debug(f"Received authentication request for user: {request.full_name}")
        auth_handler = AuthHandler()
        
        try:
            logger.debug("Initiating authentication verification")
            is_authenticated, user_id, error_message = auth_handler.verify_gitlab_auth(
                full_name=request.full_name,
                token=request.token,
                captcha_session_id=request.captcha_session_id,
                captcha_text=request.captcha_text
            )
        except ValueError as ve:
            # Handle captcha validation errors
            logger.warning(f"Captcha validation failed: {str(ve)}")
            raise HTTPException(
                status_code=400,
                detail=str(ve)
            )
        
        if is_authenticated:
            logger.debug(f"Authentication successful for user_id: {user_id}")
            return res_auth.AuthResponse(
                status=constants.ResponseStates.SUCCESS,
                message="Authentication successful",
                body={
                    "authenticated": True,
                    "user_id": user_id
                }
            )
        else:
            logger.warning(f"Authentication failed for user: {request.full_name} - {error_message}")
            raise HTTPException(
                status_code=401,
                detail=error_message or "Invalid credentials"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )


@router_auth.get("/captcha",
                response_model=res_auth.CaptchaResponse)
async def generate_captcha():
    """Generate a new captcha image"""
    try:
        logger.debug("Generating new captcha")
        captcha_handler = CaptchaHandler()
        captcha_data = captcha_handler.generate_captcha()
        
        logger.debug(f"Captcha generated successfully with session ID: {captcha_data['session_id']}")
        return res_auth.CaptchaResponse(
            status=constants.ResponseStates.SUCCESS,
            message="Captcha generated successfully",
            body={
                "session_id": captcha_data["session_id"],
                "image": captcha_data["image"]
            }
        )
            
    except Exception as e:
        logger.exception(f"Error generating captcha: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating captcha"
        ) 