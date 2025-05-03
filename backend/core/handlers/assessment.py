import os
import random
from datetime import datetime
import uuid
import json
from typing import List, Dict
from utils.mongo_utility import MongoDBClient
from utils.postgres_utility import PostgresClient
from utils.logger_utility import logger
from utils.common_utils import CommonUtils
from core.handlers.data_gen import PrepareCodingTask
from constants.configurations import MCQ_COLLECTION, USER_COLLECTION


class AssessmentHandler:
    def __init__(self):
        try:
            self._cu_ = CommonUtils()

            # Initialize MongoDB client
            self.mongo_client = MongoDBClient()
            self.mcq_collection = self.mongo_client.get_collection(MCQ_COLLECTION)
            self.user_collection = self.mongo_client.get_collection(USER_COLLECTION)
            logger.debug("MongoDB connection initialized in AssessmentHandler")
            
            # Initialize Postgres client
            self.postgres_client = PostgresClient()
            logger.debug("PostgreSQL connection initialized in AssessmentHandler")
            
            # Ensure transaction table exists
            self._ensure_transaction_table()
            
        except Exception as e:
            logger.error(f"Failed to initialize Assessment handler: {str(e)}")
            raise

    def _ensure_transaction_table(self):
        """Create transactions schema and mcq_transactions table if they don't exist"""
        try:
            logger.debug("Attempting to create transactions schema if not exists")
            create_schema_query = """
            CREATE SCHEMA IF NOT EXISTS transactions;
            """
            self.postgres_client.execute_query(create_schema_query)
            logger.debug("Successfully ensured transactions schema exists")

            logger.debug("Attempting to create mcq_transactions table if not exists")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS transactions.mcq_transactions (
                transaction_id UUID PRIMARY KEY,
                user_id INTEGER,
                question_id VARCHAR(255),
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR(255),
                arguments JSONB,
                correct_response JSONB,
                user_response JSONB
            );
            """
            self.postgres_client.execute_query(create_table_query)
            logger.debug("Successfully ensured transactions.mcq_transactions table exists")
            
        except Exception as e:
            logger.error(f"Error creating schema/table: {str(e)}")
            raise

    def generate_user_data(self, task_id, **kwargs):
        num_samples = 10000
        seed = kwargs.get("seed", 1729)
        constraint = kwargs.get("constraint", 10)

        path = kwargs.get("path", None)
        ref_path = os.path.join("assets", "responses")

        self._cu_.make_dirs(path)

        try:

            prep_obj = PrepareCodingTask(ref_path=ref_path, path=path, seed=seed)

            kwargs["num_samples"] = num_samples
            out = getattr(prep_obj, task_id)(**kwargs)
            # prep_obj.coding_task_1()
            # prep_obj.coding_task_2(num_samples=num_samples)
            # prep_obj.coding_task_3(num_samples=num_samples)
            # prep_obj.coding_task_4(num_samples=num_samples)
            return path, seed, constraint, out
        except Exception as e:
            raise Exception(e)

    def prepare_mcq_section(self, user_id):
        try:
            # Get 5 random questions from MongoDB
            pipeline = [{"$sample": {"size": 5}}]
            questions = list(self.mcq_collection.aggregate(pipeline))

            logger.debug(f"Retrieved {len(questions)} questions from MongoDB")
            if not questions:
                logger.error("No questions available in the database")
                raise ValueError("No questions available")

            # Log question IDs for debugging
            question_ids = [str(q["_id"]) for q in questions]
            logger.debug(f"Selected question IDs: {question_ids}")

            # Insert transactions into Postgres
            current_time = datetime.utcnow()
            insert_query = """
                        INSERT INTO transactions.mcq_transactions (
                            transaction_id, user_id, question_id, start_time, status, correct_response
                        ) VALUES %s
                        """

            # Prepare values for bulk insert
            values = []
            for question in questions:
                transaction_id = uuid.uuid4()
                correct_answer = question.get("correct_answer", [])
                # Ensure correct_answer is a list and convert to JSON string
                if not isinstance(correct_answer, list):
                    correct_answer = [correct_answer] if correct_answer else []
                logger.debug(f"Preparing transaction - ID: {transaction_id}, Question ID: {question['_id']},"
                             f" Correct Answer: {correct_answer}")
                values.append((
                    str(transaction_id),
                    user_id,
                    str(question["_id"]),
                    None,
                    'pending',
                    json.dumps(correct_answer)  # Convert list to JSON string for JSONB
                ))

            logger.debug(f"Attempting to insert {len(values)} transactions into PostgreSQL")
            # Execute bulk insert
            self.postgres_client.execute_many(insert_query, values)
            logger.debug(f"Successfully inserted {len(values)} transactions for user {user_id}")
        except Exception as e:
            pass

    def prepare_coding_section(self, user_id, seed, constraint, path):
        try:
            tasks = [
                {"_id": "coding_task_1",
                 "question": f"""You are given a zip file that can be downloaded.
                  The zip file contains a Jupyter notebook with the details of the task. 
                  The seed for your task should be set to `{seed}`"""},
                {"_id": "coding_task_2",
                 "question": f"""You are given a zip file that can be downloaded.
                  The zip file contains a Jupyter notebook with the details of the task and a dataset for you to use as the input for your task.
                  The seed for your task should be set to `{seed}`"""},
                {"_id": "coding_task_3",
                 "question": f"""You are given a zip file that can be downloaded.
                  The zip file contains a Jupyter notebook with the details of the task and a dataset for you to use as the input for your task.
                  The seed for your task should be set to `{seed}`"""},
                {"_id": "coding_task_4",
                 "question": f"""You are given a zip file that can be downloaded.
                  The zip file contains a Jupyter notebook with the details of the task and a dataset for you to use as the input for your task. 
                  The seed for your task should be set to `{seed}`. Your target planet is `##TARGET##`. The distance constraint should be set to `{constraint}`"""}
            ]

            insert_query = """
            INSERT INTO transactions.mcq_transactions (
            transaction_id, user_id, question_id, start_time, status, arguments)
             VALUES %s
             """

            values = []
            for task in tasks:
                task_id = task["_id"]
                question = task["question"]
                logger.debug(f"Preparing coding task {task_id}")
                path, seed, constraint, out = self.generate_user_data(task_id=task_id, path=path)
                # Generate user data
                transaction_id = uuid.uuid4()
                values.append((
                    str(transaction_id),
                    user_id,
                    str(task_id),
                    None,
                    'pending',
                    json.dumps({"seed": seed,
                                "constraint": constraint,
                                "path": path,
                                "gen_data_out": out,
                                "question": question.replace('##TARGET##', str(out))})  # Convert list to JSON string for JSONB
                ))

            logger.debug(f"Attempting to coding task {len(values)} transactions into PostgreSQL")
            # Execute bulk insert
            self.postgres_client.execute_many(insert_query, values)
            return True
        except Exception as e:
            logger.warning(f"There was a problem when preparing the coding tasks: {e}", exc_info=True)
            return False

    def start_assessment(self, user_id: str, start_epoch: int) -> bool:
        """
        Start a new assessment for a user or return active assessment questions
        
        Args:
            user_id: The ID of the user taking the assessment
            start_epoch: Epoch time when assessment started
            
        Returns:
            bool: True if assessment started successfully
            
        Raises:
            ValueError: If user not found or if no questions are available
        """
        try:
            user_id = int(user_id)
            seed = random.randint(1, 1000)
            constraint = random.randint(5, 25)
            path = os.path.join("gen_data", f"seed_{seed}_constraint_{constraint}")

            logger.debug(f"Starting assessment for user_id: {user_id}")
            
            # Check user's assessment status
            user = self.user_collection.find_one({"user_id": user_id})
            if not user:
                logger.error(f"User {user_id} not found in database")
                raise ValueError("User not found")
                
            if user.get("started_assessment", {}).get("status", False):
                logger.info(f"User {user_id} has an active assessment, fetching existing questions")
                # Fetch existing questions from PostgreSQL
                fetch_query = """
                SELECT question_id FROM transactions.mcq_transactions 
                WHERE user_id = %s AND end_time IS NULL
                ORDER BY start_time DESC LIMIT 5
                """
                question_ids = self.postgres_client.fetch_all(fetch_query, (user_id,))
                
                if not question_ids:
                    logger.warning(f"No active questions found for user {user_id}, starting new assessment")
                else:
                    # Get questions from MongoDB using the stored IDs
                    questions = []
                    for (q_id,) in question_ids:
                        question = self.mcq_collection.find_one({"_id": q_id})
                        if question:
                            question["_id"] = str(question["_id"])
                            question.pop("correct_answer", None)
                            questions.append(question)
                    
                    if questions:
                        logger.debug(f"Found {len(questions)} existing questions for user {user_id}")
                        return questions
                    else:
                        logger.warning(f"Could not find questions in MongoDB, starting new assessment")

            self.prepare_mcq_section(user_id=user_id)
            self.prepare_coding_section(user_id=user_id, seed=seed, constraint=constraint, path=path)

            # Update user's assessment status with start time
            self.user_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "started_assessment": {
                        "status": True,
                        "start_time": start_epoch
                    }
                }}
            )
            logger.debug(f"Updated assessment status for user {user_id}")

            logger.debug("Assessment setup completed successfully")
            return True
            
        except ValueError as ve:
            logger.warning(f"Validation error in start_assessment: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error starting assessment: {str(e)}", exc_info=True)
            raise
