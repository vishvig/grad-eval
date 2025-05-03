import os
import json
from datetime import datetime
from fastapi import UploadFile
from typing import Optional, Dict
from utils.postgres_utility import PostgresClient
from utils.git_utility import get_git_provider
from utils.logger_utility import logger


class CodingTaskHandler:
    def __init__(self):
        try:
            # Initialize Postgres client
            self.postgres_client = PostgresClient()
            logger.debug("PostgreSQL connection initialized in CodingTaskHandler")
            
            # Initialize Git provider
            self.git_provider = get_git_provider()
            logger.debug("Git provider initialized in CodingTaskHandler")
            
        except Exception as e:
            logger.error(f"Failed to initialize Coding Task handler: {str(e)}")
            raise

    def get_task_file_path(self, user_id: str, question_id: str) -> str:
        """
        Get the file path for a coding task zip file
        
        Args:
            user_id: The ID of the user
            question_id: The ID of the question/task
            
        Returns:
            str: Path to the zip file
            
        Raises:
            ValueError: If the task is not found or if arguments are invalid
        """
        try:
            user_id = int(user_id)
            logger.debug(f"Fetching task file path for user_id: {user_id}, question_id: {question_id}")
            
            # Fetch task arguments from PostgreSQL
            fetch_query = f"""
            SELECT arguments FROM transactions.mcq_transactions 
            WHERE user_id = {user_id} AND question_id = '{question_id}'
            LIMIT 1
            """
            result = self.postgres_client.fetch_one(fetch_query)
            
            if not result:
                logger.error(f"No task found for user {user_id} and question {question_id}")
                raise ValueError("Task not found")
                
            arguments = result[0]
            if not arguments:
                logger.error(f"No arguments found for task")
                raise ValueError("Task arguments not found")
                
            # Get the path from arguments
            path = arguments.get("path")
            if not path:
                logger.error("Path not found in arguments")
                raise ValueError("Task path not found")
                
            # Construct the zip file path
            zip_file_path = os.path.join(path, f"{question_id.replace('_', '-')}.zip")
            
            # Check if file exists
            if not os.path.isfile(zip_file_path):
                logger.error(f"Zip file not found at path: {zip_file_path}")
                raise ValueError("Task file not found")
                
            logger.debug(f"Found task file at path: {zip_file_path}")
            return zip_file_path
            
        except ValueError as ve:
            logger.warning(f"Validation error in get_task_file_path: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error getting task file path: {str(e)}", exc_info=True)
            raise

    async def commit_task_files(
        self,
        user_id: str,
        question_id: str,
        solution_file: Optional[UploadFile] = None,
        notebook_file: Optional[UploadFile] = None
    ) -> None:
        """
        Commit task files to Git repository. Both files will be committed together
        under the same folder with standardized naming.
        
        Args:
            user_id: The ID of the user
            question_id: The ID of the question/task
            solution_file: The CSV solution file to commit
            notebook_file: The Jupyter notebook file to commit
            
        Raises:
            ValueError: If the files cannot be committed
        """
        try:
            user_id = int(user_id)
            logger.debug(f"Committing files for user_id: {user_id}, question_id: {question_id}")
            
            # Create or get branch for user
            branch_name = f"user-{user_id}"
            self.git_provider.ensure_branch_exists(branch_name)
            
            # Commit files if provided
            if solution_file:
                solution_content = await solution_file.read()
                file_path = f"{question_id}/{question_id}.csv"
                self.git_provider.commit_file(
                    branch_name=branch_name,
                    file_path=file_path,
                    content=solution_content,
                    commit_message=f"Submit solution for {question_id}"
                )
                
            if notebook_file:
                notebook_content = await notebook_file.read()
                file_path = f"{question_id}/{question_id}.ipynb"
                self.git_provider.commit_file(
                    branch_name=branch_name,
                    file_path=file_path,
                    content=notebook_content,
                    commit_message=f"Submit notebook for {question_id}"
                )
                
            logger.debug(f"Successfully committed files for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error committing files: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to commit files: {str(e)}")

    def get_next_task(self, user_id: str, current_question_id: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get the next coding task for a user
        
        Args:
            user_id: The ID of the user
            current_question_id: The current question ID (if any)
            
        Returns:
            Optional[Dict[str, str]]: Dictionary containing question_id and question text, or None if no more tasks
        """
        try:
            user_id = int(user_id)
            logger.debug(f"Getting next task for user_id: {user_id}, current_question_id: {current_question_id}")
            
            # If current_question_id is provided, mark it as done
            if current_question_id:
                update_query = f"""
                UPDATE transactions.mcq_transactions 
                SET status = 'done', end_time = NOW()
                WHERE user_id = {user_id}::INTEGER AND question_id = '{current_question_id}'
                """
                self.postgres_client.execute_query(update_query)
                logger.debug(f"Marked question {current_question_id} as done for user {user_id}")
            
            # Check if all tasks are done first
            all_tasks_query = f"""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed
            FROM transactions.mcq_transactions 
            WHERE user_id = {user_id}::INTEGER AND question_id LIKE 'coding_task_%'
            """
            result = self.postgres_client.fetch_one(all_tasks_query)
            
            # If we have tasks and all are done, return None
            if result and result[0] > 0 and result[0] == result[1]:
                logger.debug(f"All coding tasks completed for user {user_id}")
                return dict()
            
            # Check if any task is in progress
            in_progress_query = f"""
            SELECT question_id, arguments FROM transactions.mcq_transactions 
            WHERE user_id = {user_id}::INTEGER AND status = 'in-progress'
            AND question_id LIKE 'coding_task_%'
            LIMIT 1
            """
            in_progress_result = self.postgres_client.fetch_one(in_progress_query)
            
            if in_progress_result and in_progress_result[0]:
                # Return the in-progress task with question text
                question_id = in_progress_result[0]
                arguments = in_progress_result[1]
                question_text = arguments.get('question', '') if arguments else ''
                logger.debug(f"Found in-progress task: {question_id} for user {user_id}")
                return {
                    'question_id': question_id,
                    'question': question_text
                }
            
            # Get the first incomplete task
            next_task_query = f"""
            SELECT question_id, arguments FROM transactions.mcq_transactions 
            WHERE user_id = {user_id}::INTEGER 
            AND status != 'done' 
            AND question_id LIKE 'coding_task_%'
            ORDER BY question_id ASC
            LIMIT 1
            """
            next_task = self.postgres_client.fetch_one(next_task_query)
            
            if next_task:
                next_question_id = next_task[0]
                arguments = next_task[1]
                question_text = arguments.get('question', '') if arguments else ''
                
                # Update status to in-progress
                update_query = f"""
                UPDATE transactions.mcq_transactions 
                SET status = 'in-progress', start_time = NOW()
                WHERE user_id = {user_id}::INTEGER AND question_id = '{next_question_id}'
                """
                self.postgres_client.execute_query(update_query)
                logger.debug(f"Marked question {next_question_id} as in-progress for user {user_id}")
                
                return {
                    'question_id': next_question_id,
                    'question': question_text
                }
            else:
                # No incomplete tasks found
                logger.debug(f"No incomplete tasks found for user {user_id}")
                return dict()
            
        except Exception as e:
            logger.error(f"Error getting next task: {str(e)}", exc_info=True)
            raise
