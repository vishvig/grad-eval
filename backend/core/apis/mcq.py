from fastapi import FastAPI, APIRouter, Request, HTTPException, Header
from typing import Optional

from constants import constants
from ..handlers.mcq import MCQHandler
from ..handlers.assessment import AssessmentHandler
from ..schemas.responses import mcq as res_mcq
from ..schemas.requests import mcq as req_mcq
from utils.logger_utility import logger

router_mcq = APIRouter(prefix=constants.Routes.MCQ)


@router_mcq.post(constants.Apis.NEXT_QUESTION,
                 response_model=res_mcq.NextQuestionResponse)
async def next_question(request: req_mcq.NextQuestion):
    """Get the next question from the database"""
    try:
        if not request.user_id:
            raise HTTPException(
                status_code=401,
                detail="User ID is required"
            )

        logger.debug(f"Fetching next question: {request.user_id}")
        res = MCQHandler().get_next_question(user_id=request.user_id)
        return res_mcq.NextQuestionResponse(
            status=constants.ResponseStates.SUCCESS,
            message="Successfully fetched next question",
            body=res
        )

    except ValueError as ve:
        logger.warning(f"Error starting assessment: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unexpected error starting assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while starting assessment"
        )


@router_mcq.post(constants.Apis.SUBMIT_RESPONSE,
                 response_model=res_mcq.NextQuestionResponse)
async def submit_response(request: req_mcq.AnswerSubmission):
    """Get the next question from the database"""
    try:
        if not request.user_id:
            raise HTTPException(
                status_code=401,
                detail="User ID is required"
            )

        logger.debug(f"Submitting user's response: {request.user_id}")
        MCQHandler().submit_response(user_id=request.user_id,
                                     question_id=request.question_id,
                                     selected_responses=request.selected_answers)
        return res_mcq.DefaultResponse(
            status=constants.ResponseStates.SUCCESS,
            message="Successfully submitted response"
        )

    except ValueError as ve:
        logger.warning(f"Error submitting response: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unexpected error when submitting the response: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while hen submitting the response"
        )


@router_mcq.post(constants.Apis.START_ASSESSMENT,
                 response_model=res_mcq.StartAssessmentResponse)
async def start_assessment(request: req_mcq.StartAssessmentRequest):
    """Start a new assessment for the authenticated user"""
    try:
        if not request.user_id:
            raise HTTPException(
                status_code=401,
                detail="User ID is required"
            )

        logger.debug(f"Starting assessment for user: {request.user_id}")
        assessment_handler = AssessmentHandler()
        assessment_handler.start_assessment(
            user_id=request.user_id,
            start_epoch=request.start_epoch
        )

        return res_mcq.StartAssessmentResponse(
            status=constants.ResponseStates.SUCCESS,
            message="Assessment started successfully"
        )

    except ValueError as ve:
        logger.warning(f"Error starting assessment: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unexpected error starting assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while starting assessment"
        )
