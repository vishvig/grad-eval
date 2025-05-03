import abc
import base64
import requests
import json
from typing import Optional, Tuple, Dict
from utils.logger_utility import logger
from constants.configurations import (
    GIT_PROVIDER,
    GITLAB_SERVER_URL,
    GITLAB_API_VERSION,
    GITLAB_PROJECT_ID,
    GITLAB_ACCESS_TOKEN,
    GITHUB_API_URL,
    GITHUB_REPO,
    GITHUB_ACCESS_TOKEN
)


class GitProvider(abc.ABC):
    """Abstract base class for git providers"""
    
    @abc.abstractmethod
    def verify_token(self) -> Tuple[bool, Dict]:
        """Verify the access token"""
        pass
        
    @abc.abstractmethod
    def commit_file(self, branch_name: str, file_path: str, content: bytes, commit_message: str) -> bool:
        """Commit a file to the repository"""
        pass
        
    @abc.abstractmethod
    def ensure_branch_exists(self, branch_name: str) -> None:
        """Ensure a branch exists, create if it doesn't"""
        pass


class GitLabProvider(GitProvider):
    """GitLab implementation"""
    
    def __init__(self):
        self.access_token = GITLAB_ACCESS_TOKEN
        self.base_url = f"{GITLAB_SERVER_URL}/api/{GITLAB_API_VERSION}"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
    def verify_token(self) -> Tuple[bool, Dict]:
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                logger.warning(f"Failed to verify GitLab token. Status code: {response.status_code}")
                return False, {}
                
        except Exception as e:
            logger.error(f"Error verifying GitLab token: {str(e)}")
            return False, {}
            
    def commit_file(self, branch_name: str, file_path: str, content: bytes, commit_message: str) -> bool:
        try:
            self.ensure_branch_exists(branch_name)
            
            content_base64 = base64.b64encode(content).decode('utf-8')
            
            url = f"{self.base_url}/projects/{GITLAB_PROJECT_ID}/repository/files/{file_path}"
            data = {
                "branch": branch_name,
                "content": content_base64,
                "commit_message": commit_message,
                "encoding": "base64"
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.debug(f"Successfully committed file {file_path} to branch {branch_name}")
                return True
            else:
                logger.warning(f"Failed to commit file. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing file: {str(e)}")
            return False
            
    def ensure_branch_exists(self, branch_name: str) -> None:
        try:
            url = f"{self.base_url}/projects/{GITLAB_PROJECT_ID}/repository/branches/{branch_name}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                create_url = f"{self.base_url}/projects/{GITLAB_PROJECT_ID}/repository/branches"
                data = {
                    "branch": branch_name,
                    "ref": "master"
                }
                response = requests.post(create_url, headers=self.headers, json=data)
                
                if response.status_code in [200, 201]:
                    logger.debug(f"Created new branch: {branch_name}")
                else:
                    logger.error(f"Failed to create branch. Status code: {response.status_code}")
                    raise Exception("Failed to create branch")
                    
        except Exception as e:
            logger.error(f"Error ensuring branch exists: {str(e)}")
            raise


class GitHubProvider(GitProvider):
    """GitHub implementation"""
    
    def __init__(self):
        self.access_token = GITHUB_ACCESS_TOKEN
        self.base_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.debug(f"Initialized GitHub provider with repo: {GITHUB_REPO}")
        
        # Verify repository access
        logger.debug("Verifying repository access...")
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Failed to access repository. Status code: {response.status_code}")
            try:
                error_details = response.json()
                logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
            except:
                logger.error(f"Raw error response: {response.text}")
            raise Exception("Failed to access repository. Please check if the repository exists and you have the correct permissions.")
            
        repo_data = response.json()
        self.default_branch = repo_data.get('default_branch', 'main')
        logger.debug(f"Repository access verified. Default branch: {self.default_branch}")
        
    def verify_token(self) -> Tuple[bool, Dict]:
        try:
            logger.debug("Verifying GitHub token...")
            response = requests.get(f"{GITHUB_API_URL}/user", headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.debug(f"Token verification successful. Authenticated as: {user_data.get('login')}")
                return True, response.json()
            else:
                logger.warning(f"Failed to verify GitHub token. Status code: {response.status_code}")
                try:
                    error_details = response.json()
                    logger.warning(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    logger.warning(f"Raw error response: {response.text}")
                return False, {}
                
        except Exception as e:
            logger.error(f"Error verifying GitHub token: {str(e)}")
            return False, {}
            
    def commit_file(self, branch_name: str, file_path: str, content: bytes, commit_message: str) -> bool:
        try:
            self.ensure_branch_exists(branch_name)
            
            content_base64 = base64.b64encode(content).decode('utf-8')
            
            # First, check if file exists to get the SHA if it does
            url = f"{self.base_url}/contents/{file_path}"
            logger.debug(f"Checking if file exists at: {url}?ref={branch_name}")
            response = requests.get(f"{url}?ref={branch_name}", headers=self.headers)
            
            if response.status_code == 200:
                logger.debug(f"File exists, getting SHA")
                sha = response.json().get('sha')
            else:
                logger.debug(f"File does not exist (status code: {response.status_code})")
                sha = None
            
            data = {
                "message": commit_message,
                "content": content_base64,
                "branch": branch_name
            }
            
            if sha:
                data["sha"] = sha
                logger.debug(f"Using existing file SHA: {sha}")
            
            logger.debug(f"Committing file to: {url}")
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.debug(f"Successfully committed file {file_path} to branch {branch_name}")
                return True
            else:
                logger.warning(f"Failed to commit file. Status code: {response.status_code}")
                try:
                    error_details = response.json()
                    logger.warning(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    logger.warning(f"Raw error response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing file: {str(e)}")
            return False
            
    def ensure_branch_exists(self, branch_name: str) -> None:
        try:
            # Check if branch exists
            url = f"{self.base_url}/branches/{branch_name}"
            logger.debug(f"Checking if branch exists: {url}")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                logger.debug(f"Branch {branch_name} does not exist, creating it...")
                # Get default branch reference
                ref_url = f"{self.base_url}/git/refs/heads/{self.default_branch}"
                logger.debug(f"Getting default branch reference: {ref_url}")
                ref_response = requests.get(ref_url, headers=self.headers)
                
                if ref_response.status_code != 200:
                    logger.error(f"Failed to get default branch reference. Status code: {ref_response.status_code}")
                    try:
                        error_details = ref_response.json()
                        logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
                    except:
                        logger.error(f"Raw error response: {ref_response.text}")
                    raise Exception("Failed to get default branch reference")
                
                base_sha = ref_response.json()['object']['sha']
                logger.debug(f"Using {self.default_branch} as base branch with SHA: {base_sha}")
                
                # Create new branch
                create_url = f"{self.base_url}/git/refs"
                data = {
                    "ref": f"refs/heads/{branch_name}",
                    "sha": base_sha
                }
                logger.debug(f"Creating new branch from {self.default_branch}. URL: {create_url}, Data: {json.dumps(data, indent=2)}")
                response = requests.post(create_url, headers=self.headers, json=data)
                
                if response.status_code in [200, 201]:
                    logger.debug(f"Created new branch: {branch_name}")
                else:
                    error_msg = f"Failed to create branch. Status code: {response.status_code}"
                    if response.status_code == 404:
                        error_msg += ". Please check if the repository exists and you have the correct permissions."
                    logger.error(error_msg)
                    try:
                        error_details = response.json()
                        logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
                    except:
                        logger.error(f"Raw error response: {response.text}")
                    raise Exception(error_msg)
            else:
                logger.debug(f"Branch {branch_name} already exists")
                    
        except Exception as e:
            logger.error(f"Error ensuring branch exists: {str(e)}")
            raise


def get_git_provider() -> GitProvider:
    """Factory function to get the configured git provider"""
    if GIT_PROVIDER.lower() == "gitlab":
        return GitLabProvider()
    elif GIT_PROVIDER.lower() == "github":
        return GitHubProvider()
    else:
        raise ValueError(f"Unsupported git provider: {GIT_PROVIDER}") 