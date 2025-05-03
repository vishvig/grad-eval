from datetime import datetime
# from utils.gitlab_utility import GitlabClient
from utils.mongo_utility import MongoDBClient
from utils.logger_utility import logger
from constants.configurations import (
    AUTH_AUDIT_COLLECTION,
    USER_COLLECTION,
    GITLAB_SERVER_URL,
    GITLAB_API_VERSION
)
from typing import Dict, Optional, Tuple, Union
from .captcha import CaptchaHandler
import requests
import json


class AuthHandler:
    def __init__(self):
        try:
            self.mongo_client = MongoDBClient()
            self.audit_collection = self.mongo_client.get_collection(AUTH_AUDIT_COLLECTION)
            self.user_collection = self.mongo_client.get_collection(USER_COLLECTION)
            self.gitlab_url = GITLAB_SERVER_URL
            self.gitlab_api_version = GITLAB_API_VERSION
            self.captcha_handler = CaptchaHandler()
            logger.debug(f"AuthHandler initialized with GitLab URL: {self.gitlab_url}, API Version: {self.gitlab_api_version}")
        except Exception as e:
            logger.error(f"Failed to initialize Auth handler: {str(e)}")
            raise

    def verify_gitlab_auth(self, full_name: str, token: str, captcha_session_id: str, captcha_text: str) -> Tuple[bool, Union[str, None], Optional[str], Optional[Dict]]:
        """
        Verify user authentication with Gitlab and validate captcha
        
        Args:
            full_name (str): User's full name
            token (str): Access token
            captcha_session_id (str): Session ID of the captcha to verify
            captcha_text (str): User's input for captcha verification
            
        Returns:
            Tuple[bool, Union[str, None], Optional[str], Optional[Dict]]: (is_authenticated, user_id, error_message, assessment_info)
                - is_authenticated: True if authentication successful, False otherwise
                - user_id: User's ID if authentication successful, None otherwise
                - error_message: None if successful, otherwise contains the specific error message
                - assessment_info: Dict containing assessment status and start time if available
            
        Raises:
            ValueError: If captcha verification fails
            Exception: For any other errors during authentication
        """
        try:
            logger.debug(f"Starting authentication for user: {full_name}")
            logger.debug(f"Captcha session ID: {captcha_session_id}")
            
            # First verify captcha
            logger.debug("Verifying captcha...")
            if not self.captcha_handler.verify_captcha(captcha_session_id, captcha_text):
                logger.warning(f"Captcha verification failed for session: {captcha_session_id}")
                raise ValueError("Invalid captcha")
            logger.debug("Captcha verification successful")

            # Then verify credentials using REST API
            api_url = f"{self.gitlab_url}/api/{self.gitlab_api_version}/user"
            headers = {"Authorization": f"Bearer {token}"}
            
            logger.debug(f"Making GitLab API request to: {api_url}")
            response = requests.get(api_url, headers=headers)
            
            logger.debug(f"GitLab API response status code: {response.status_code}")
            if response.status_code != 200:
                logger.warning(f"GitLab API request failed. Status code: {response.status_code}")
                try:
                    error_details = response.json()
                    logger.warning(f"Error response: {json.dumps(error_details, indent=2)}")
                except:
                    logger.warning(f"Raw error response: {response.text}")
                return False, None, "Invalid token or API error", None
            
            # Get user info and verify name
            user_data = response.json()
            logger.debug(f"GitLab API response data: {json.dumps(user_data, indent=2)}")
            
            api_full_name = user_data.get("name", "").lower()
            provided_full_name = full_name.lower()
            logger.debug(f"Comparing names - API: '{api_full_name}', Provided: '{provided_full_name}'")
            
            if api_full_name != provided_full_name:
                logger.warning(f"Name mismatch - API: '{api_full_name}', Provided: '{provided_full_name}'")
                error_msg = f"The provided name '{full_name}' does not match the name '{user_data.get('name')}' associated with this token"
                return False, None, error_msg, None
                
            # Store user details and get assessment info
            logger.debug("Authentication successful, updating user details")
            assessment_info = self._update_user_details(user_data)
            
            # Return success with user_id and assessment info
            user_id = str(user_data.get("id"))
            return True, user_id, None, assessment_info
            
        except ValueError as ve:
            # Re-raise captcha validation errors
            raise
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}", exc_info=True)
            return False, None, "An unexpected error occurred during authentication", None

    def _update_user_details(self, user_data: Dict) -> Dict:
        """Update user details in MongoDB and return assessment info"""
        try:
            user_id = int(user_data.get("id"))
            logger.debug(f"Updating details for user ID: {user_id}")
            
            # Get existing user data
            existing_user = self.user_collection.find_one({"user_id": int(user_id)})
            
            # Get assessment status and start time
            assessment_info = {
                "status": False,
                "start_time": None
            }
            if existing_user:
                logger.debug(f"User {user_id} found in database. Fetching assessment status.")
                started_assessment = existing_user.get("started_assessment", dict())
                assessment_info["status"] = started_assessment.get("status", False)
                assessment_info["start_time"] = started_assessment.get("start_time", None)
            
            # Update user details
            update_result = self.user_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "name": user_data.get("name"),
                        "username": user_data.get("username"),
                        "email": user_data.get("email"),
                        "last_login": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "started_assessment.status": False,
                        "started_assessment.assessment_start_time": None
                    }
                },
                upsert=True
            )
            
            logger.debug(f"User details update result - Modified: {update_result.modified_count}, Upserted: {update_result.upserted_id is not None}")
            
            return assessment_info
            
        except Exception as e:
            logger.error(f"Error updating user details: {str(e)}")
            return {"status": False, "start_time": None}

    async def verify_token(self, token: str):
        try:
            # Verify the token and get user data
            user_data = await self._verify_token(token)
            
            return {
                "status": "success",
                "message": "Token verified successfully",
                "user_id": user_data.get("user_id"),  # Include user_id in response
                # Include other necessary user data
            }
        except Exception as e:
            raise AuthenticationError(str(e))
