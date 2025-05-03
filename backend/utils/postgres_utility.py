import psycopg2
from psycopg2.extras import execute_values
from constants.configurations import POSTGRES_URI, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from utils.logger_utility import logger


class PostgresClient:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresClient, cls).__new__(cls)
            logger.debug("Creating new PostgresClient instance")
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            if self._conn is None or self._conn.closed:
                logger.debug(f"Initializing PostgreSQL connection with URI: {POSTGRES_URI}")
                self._conn = psycopg2.connect(POSTGRES_URI)
                logger.info("Successfully connected to PostgreSQL")
                logger.debug("Connection details - Database: %s, User: %s", POSTGRES_DB, POSTGRES_USER)
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}", exc_info=True)
            raise

    @property
    def conn(self):
        """Get the database connection, reinitializing if necessary"""
        self._initialize_connection()
        return self._conn

    def execute_query(self, query: str, params=None):
        """Execute a single query"""
        try:
            logger.debug(f"Executing query: {query}")
            if params:
                logger.debug(f"Query parameters: {params}")
            
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                logger.debug("Query executed successfully")
                
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error executing query: {str(e)}", exc_info=True)
            logger.error(f"Failed query: {query}")
            if params:
                logger.error(f"Failed query parameters: {params}")
            raise

    def execute_many(self, query: str, values: list):
        """Execute a query with multiple values"""
        try:
            logger.debug(f"Executing bulk query: {query}")
            logger.debug(f"Number of value sets to insert: {len(values)}")
            logger.debug(f"First value set (sample): {values[0] if values else 'No values'}")
            
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, values)
                self.conn.commit()
                logger.debug(f"Bulk query executed successfully, inserted {len(values)} records")
                
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error executing bulk query: {str(e)}", exc_info=True)
            logger.error(f"Failed query: {query}")
            logger.error(f"Number of values that failed to insert: {len(values)}")
            raise

    def fetch_one(self, query: str, params=None):
        """Fetch a single row"""
        try:
            logger.debug(f"Executing fetch_one query: {query}")
            if params:
                logger.debug(f"Query parameters: {params}")
                
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                logger.debug(f"Fetch one result: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Error fetching row: {str(e)}", exc_info=True)
            raise

    def fetch_all(self, query: str, params=None):
        """Fetch all rows"""
        try:
            logger.debug(f"Executing fetch_all query: {query}")
            if params:
                logger.debug(f"Query parameters: {params}")
                
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug(f"Fetch all returned {len(results)} rows")
                return results
                
        except Exception as e:
            logger.error(f"Error fetching rows: {str(e)}", exc_info=True)
            raise

    def close(self):
        """Close the database connection"""
        if hasattr(self, '_conn') and self._conn is not None:
            logger.debug("Closing PostgreSQL connection")
            self._conn.close()
            self._conn = None
            logger.debug("PostgreSQL connection closed successfully") 