from datetime import datetime, timedelta
import uuid
from utils.captcha_utility import CaptchaGenerator
from utils.mongo_utility import MongoDBClient
from utils.logger_utility import logger
from constants.configurations import CAPTCHA_SESSIONS_COLLECTION


class CaptchaHandler:
    def __init__(self):
        try:
            self.captcha_generator = CaptchaGenerator()
            self.mongo_client = MongoDBClient()
            self.sessions_collection = self.mongo_client.get_collection(CAPTCHA_SESSIONS_COLLECTION)
            
            # Create TTL index if it doesn't exist
            self._ensure_ttl_index()
            
        except Exception as e:
            logger.error(f"Failed to initialize Captcha handler: {str(e)}")
            raise

    def _ensure_ttl_index(self):
        """Ensure TTL index exists on expiry field"""
        try:
            self.sessions_collection.create_index(
                "expiry",
                expireAfterSeconds=0,
                background=True
            )
        except Exception as e:
            logger.warning(f"Failed to create TTL index: {str(e)}")

    def generate_captcha(self) -> dict:
        """
        Generate a new captcha and store session
        
        Returns:
            dict: Contains session_id and base64 image
        """
        try:
            # Generate captcha
            text, image_data = self.captcha_generator.generate_captcha()
            
            # Create session
            session_id = str(uuid.uuid4())
            expiry = datetime.utcnow() + timedelta(minutes=10)  # Session expires in 10 minutes
            
            # Store in MongoDB
            session_data = {
                "session_id": session_id,
                "captcha_text": text,
                "created_at": datetime.utcnow(),
                "expiry": expiry,
                "is_used": False
            }
            self.sessions_collection.insert_one(session_data)
            
            return {
                "session_id": session_id,
                "image": image_data
            }
            
        except Exception as e:
            logger.error(f"Error generating captcha: {str(e)}")
            raise

    def verify_captcha(self, session_id: str, captcha_text: str) -> bool:
        """
        Verify a captcha response
        
        Args:
            session_id: The session ID
            captcha_text: The user's captcha response
            
        Returns:
            bool: Whether the captcha was correct
        """
        try:
            # Find and update the session
            result = self.sessions_collection.find_one_and_update(
                {
                    "session_id": session_id,
                    "is_used": False,
                    "expiry": {"$gt": datetime.utcnow()}
                },
                {"$set": {"is_used": True}},
                return_document=True
            )
            
            if not result:
                return False
                
            return result["captcha_text"].upper() == captcha_text.upper()
            
        except Exception as e:
            logger.error(f"Error verifying captcha: {str(e)}")
            return False 