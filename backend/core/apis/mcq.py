from fastapi import FastAPI, APIRouter, Request, HTTPException, Header
from typing import Optional

from constants import constants
from ..handlers.mcq import MCQHandler
from ..handlers.assessment import AssessmentHandler
from ..schemas.responses import mcq as res_mcq
from ..schemas.requests import mcq as req_mcq
from utils.logger_utility import logger

router_mcq = APIRouter(prefix=constants.Routes.MCQ)


@router_mcq.get(constants.Apis.NEXT_QUESTION,
                response_model=res_mcq.NextQuestionResponse)
async def next_question():
    """Get the next question from the database"""
    res = MCQHandler().get_next_question()
    return res_mcq.NextQuestionResponse(
        status=constants.ResponseStates.SUCCESS,
        message="Successfully fetched next question",
        body=res
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
        questions = assessment_handler.start_assessment(request.user_id)
        
        # Transform questions to match response model
        formatted_questions = []
        for q in questions:
            formatted_questions.append(
                res_mcq.NextQuestionResponseModel(
                    id=q["_id"],
                    text=q["text"],
                    options=[
                        res_mcq.MCQOption(id=str(opt["id"]), text=opt["text"])
                        for opt in q["options"]
                    ],
                    allowMultiple=q.get("allowMultiple", False)
                )
            )
        
        return res_mcq.StartAssessmentResponse(
            status=constants.ResponseStates.SUCCESS,
            message="Assessment started successfully",
            body=formatted_questions
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
