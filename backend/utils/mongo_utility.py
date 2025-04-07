from pymongo import MongoClient
from constants.configurations import MONGO_URI, GRAD_EVAL_DB
from utils.logger_utility import logger


class MongoDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            try:
                cls._instance.client = MongoClient(MONGO_URI)
                cls._instance.db = cls._instance.client[GRAD_EVAL_DB]
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
        return cls._instance

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close(self):
        if hasattr(self, 'client'):
            self.client.close()
