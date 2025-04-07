from ..schemas.responses.mcq import NextQuestionResponseModel
from utils.mongo_utility import MongoDBClient
from utils.logger_utility import logger
from constants.configurations import MCQ_COLLECTION
from exceptions.mcq import NoQuestionsAvailableError, QuestionFetchError
import random


class MCQHandler(object):
    def __init__(self):
        try:
            self.mongo_client = MongoDBClient()
            self.mcq_collection = self.mongo_client.get_collection(MCQ_COLLECTION)
        except Exception as e:
            logger.error(f"Failed to initialize MCQ handler: {str(e)}")
            raise QuestionFetchError(f"Failed to initialize MCQ handler: {str(e)}")

    def get_next_question(self):
        """
        Fetches a random question from MongoDB.
        
        Returns:
            NextQuestionResponseModel: The next question with its options
            
        Raises:
            NoQuestionsAvailableError: When no questions are found in the database
            QuestionFetchError: For other database or processing errors
        """
        try:
            # Get a random question from the collection
            pipeline = [{"$sample": {"size": 1}}]
            question = list(self.mcq_collection.aggregate(pipeline))
            
            if not question:
                logger.warning("No questions found in the database")
                raise NoQuestionsAvailableError()
                
            question = question[0]
            
            # Transform the MongoDB document to our response model
            return NextQuestionResponseModel(
                id=str(question["_id"]),
                text=question["text"],
                options=[
                    {"id": str(opt["id"]), "text": opt["text"]} 
                    for opt in question["options"]
                ],
                allowMultiple=question.get("allowMultiple", False)
            )

        except NoQuestionsAvailableError:
            raise
        except Exception as e:
            logger.error(f"Error fetching next question: {str(e)}")
            raise QuestionFetchError(f"Failed to fetch next question: {str(e)}")
