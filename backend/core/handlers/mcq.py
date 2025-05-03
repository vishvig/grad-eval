import json

from ..schemas.responses.mcq import NextQuestionResponseModel
from utils.mongo_utility import MongoDBClient
from utils.logger_utility import logger
from constants.configurations import MCQ_COLLECTION
from utils.postgres_utility import PostgresClient
from exceptions.mcq import NoQuestionsAvailableError, QuestionFetchError
import random


class MCQHandler(object):
    def __init__(self):
        try:
            self.mongo_client = MongoDBClient()
            self.mcq_collection = self.mongo_client.get_collection(MCQ_COLLECTION)
            self.postgres_client = PostgresClient()
        except Exception as e:
            logger.error(f"Failed to initialize MCQ handler: {str(e)}")
            raise QuestionFetchError(f"Failed to initialize MCQ handler: {str(e)}")

    def get_next_question(self, user_id):
        """
        Fetches a random question from MongoDB.
        
        Returns:
            NextQuestionResponseModel: The next question with its options
            
        Raises:
            NoQuestionsAvailableError: When no questions are found in the database
            QuestionFetchError: For other database or processing errors
        """
        try:
            # Fetch one question where start_time is NULL
            fetch_query = """
                    SELECT question_id FROM transactions.mcq_transactions 
                    WHERE user_id = %s AND status = 'pending'
                    LIMIT 1
                """
            question_id_record = self.postgres_client.fetch_one(fetch_query, (user_id,))

            if not question_id_record:
                return NextQuestionResponseModel(
                    quizFinished=True
                )  # No questions available

            question_id = question_id_record[0]

            # Check if this is the last question
            last_question = False
            count_query = """
                    SELECT COUNT(*) FROM transactions.mcq_transactions 
                    WHERE user_id = %s AND start_time IS NULL
                """
            count_result = self.postgres_client.fetch_one(count_query, (user_id,))
            is_last_question = count_result[0] == 1  # True if only one record exists
            if is_last_question:
                last_question = True

            # Update the start_time of the fetched record
            update_query = """
                    UPDATE transactions.mcq_transactions 
                    SET start_time = NOW(), status = 'in-progress'
                    WHERE user_id = %s AND question_id = %s
                """
            self.postgres_client.execute_query(update_query, (user_id, question_id))

            _filter = {"_id": question_id}
            question = self.mcq_collection.find_one(filter=_filter)

            if not question:
                logger.warning("No questions found in the database")
                raise NoQuestionsAvailableError()

            # question = question[0]
            logger.debug(question)

            # Transform the MongoDB document to our response model
            return NextQuestionResponseModel(
                id=str(question["_id"]),
                text=question["text"],
                options=[
                    {"id": str(opt["id"]), "text": opt["text"]}
                    for opt in question["options"]
                ],
                allowMultiple=question.get("allowMultiple", False),
                lastQuestion=last_question,
                quizFinished=False
            )

        except NoQuestionsAvailableError:
            raise
        except Exception as e:
            logger.error(f"Error fetching next question: {str(e)}")
            raise QuestionFetchError(f"Failed to fetch next question: {str(e)}")

    def submit_response(self, user_id, question_id, selected_responses):
        """
        This method updates the postgres table with the user's responses for a question and
         also sets the status of the user's question to 'done'
        :param user_id: The ID if the user
        :param question_id: The ID of the question answered by the user
        :param selected_responses: The list of responses selected by the user
        :return: True or False based on the status of update
        """
        try:
            update_query = f"""
                    UPDATE transactions.mcq_transactions 
                    SET user_response = '{json.dumps(selected_responses)}', end_time = NOW(), status = 'done'
                    WHERE user_id = {user_id} AND question_id = '{question_id}'
                """
            self.postgres_client.execute_query(update_query)
            return True
        except Exception as e:
            logger.error(f"Error submitting the response: {str(e)}")
            raise
