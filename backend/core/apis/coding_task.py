import json
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from typing import Optional

from ..handlers.assessment import AssessmentHandler
from ..schemas.requests import coding_task as req_coding_task
# from ..schemas.responses import coding_task as res_coding_task
from ..handlers.coding_task import CodingTaskHandler
from utils.logger_utility import logger
from ..schemas.responses import mcq as res_mcq
from ..schemas.requests import coding_task as req_mcq
from constants import constants

router_coding_task = APIRouter(prefix=constants.Routes.CODING_TASK)


@router_coding_task.post("/download-task-file")
async def download_task_file(request: req_coding_task.DownloadTaskFileRequest) -> FileResponse:
    """Download a coding task zip file"""
    try:
        handler = CodingTaskHandler()
        file_path = handler.get_task_file_path(user_id=request.user_id, question_id=request.question_id)

        if not file_path:
            raise HTTPException(status_code=404, detail="Task file not found")

        return FileResponse(
            path=file_path,
            media_type='application/zip',
            filename=f"{request.question_id}.zip"
        )

    except ValueError as ve:
        logger.warning(f"Validation error in download_task_file: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error downloading task file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_coding_task.post("/next-task", response_model=req_coding_task.NextTaskResponse)
async def next_task(request_data: str,
                    notebook_file: Optional[UploadFile] = File(None),
                    solution_file: Optional[UploadFile] = File(None)) -> req_coding_task.NextTaskResponse:
    """Get the next coding task for a user"""
    try:
        handler = CodingTaskHandler()
        # Parse the JSON data string into a dictionary
        json_data = json.loads(request_data)
        # Validate and create the Pydantic model
        data = req_coding_task.NextTaskRequest(**json_data)

        # If files are provided, commit them to git
        if solution_file or notebook_file:
            if not data.question_id:
                raise HTTPException(status_code=400, detail="question_id is required when submitting files")

            # Commit files to git
            await handler.commit_task_files(
                user_id=data.user_id,
                question_id=data.question_id,
                solution_file=solution_file,
                notebook_file=notebook_file
            )

        # Get next task
        res = handler.get_next_task(user_id=data.user_id, current_question_id=data.question_id)

        return req_coding_task.NextTaskResponse(
            user_id=data.user_id,
            question_id=res.get("question_id", None),
            body=res.get("question", None)  # This will be None if no more tasks
        )

    except ValueError as ve:
        logger.warning(f"Validation error in next_task: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error getting next task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_coding_task.post(constants.Apis.START_ASSESSMENT,
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
        assessment_handler.start_assessment(request.user_id, start_epoch=request.start_epoch)

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
