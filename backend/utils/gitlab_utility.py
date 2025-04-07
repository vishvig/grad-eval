import requests
from constants.configurations import GITLAB_SERVER_URL, GITLAB_API_VERSION
from utils.logger_utility import logger


class GitlabClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = f"{GITLAB_SERVER_URL}/api/{GITLAB_API_VERSION}"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def verify_token(self) -> tuple[bool, dict]:
        """
        Verify the access token by making a request to get user details
        
        Returns:
            tuple[bool, dict]: (is_valid, user_details)
        """
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                logger.warning(f"Failed to verify Gitlab token. Status code: {response.status_code}")
                return False, {}
                
        except Exception as e:
            logger.error(f"Error verifying Gitlab token: {str(e)}")
            return False, {} 