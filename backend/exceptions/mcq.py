from typing import Optional


class MCQException(Exception):
    """Base exception for MCQ module"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NoQuestionsAvailableError(MCQException):
    """Raised when no questions are available in the database"""

    def __init__(self, message: str = "No questions available in the database"):
        super().__init__(message=message, status_code=500)


class QuestionFetchError(MCQException):
    """Raised when there's an error fetching questions from the database"""

    def __init__(self, message: str = "Failed to fetch question from database"):
        super().__init__(message=message, status_code=500)
