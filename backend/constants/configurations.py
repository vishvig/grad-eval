import os
import sys
from configparser import BasicInterpolation, ConfigParser
from dotenv import load_dotenv

_application_conf = "./conf/application.conf"
_default_conf = "./dev-variables.env"
load_dotenv(dotenv_path=_default_conf)
# load_dotenv()


class EnvInterpolation(BasicInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)

        if not os.path.expandvars(value).startswith("$"):
            return os.path.expandvars(value)
        else:
            return


try:
    config = ConfigParser(interpolation=EnvInterpolation())
    config.read(_application_conf)
except Exception as e:
    print(f"Error while loading the config: {e}")
    print("Failed to Load Configuration. Exiting!!!")
    sys.exit()

# API
SERVICE_HOST = config.get("API", "SERVICE_HOST", fallback="localhost")
FAST_SERVICE_PORT = config.get("API", "FAST_SERVICE_PORT", fallback=3000)

# MQTT
# BROKER_ADDRESS = config.get("MQTT", "BROKER_ADDRESS")
# BROKER_PORT = config.getint("MQTT", "BROKER_PORT")
# BROKER_USER = config.get("MQTT", "BROKER_USER")
# BROKER_PWD = config.get("MQTT", "BROKER_PWD")
# BROKER_PATH = config.get("MQTT", "BROKER_PATH")
# TIMEOUT = config.getint("MQTT", "TIMEOUT")

# LOCK_OUT_TIME_MINS = config.get("SESSION", "LOCK_OUT_TIME_MINS")

# Redis
# REDIS_URI = config.get("REDIS", "REDIS_URI")
# Redis_stream_name = config.get("REDIS", "STREAM_NAME")
# LOCK_OUT_TIME_MINS = config.get("SESSION", "LOCK_OUT_TIME_MINS")
# Mongo DB
MONGO_URI = config.get("MONGODB", "MONGO_URI")
GRAD_EVAL_DB = config.get("MONGODB", "GRAD_EVAL_DB")
MCQ_COLLECTION = config.get("MONGODB", "MCQ_COLLECTION", fallback="mcq_questions")
AUTH_AUDIT_COLLECTION = config.get("MONGODB", "AUTH_AUDIT_COLLECTION", fallback="auth_audit")
USER_COLLECTION = config.get("MONGODB", "USER_COLLECTION", fallback="users")
CAPTCHA_SESSIONS_COLLECTION = config.get("MONGODB", "CAPTCHA_SESSIONS_COLLECTION", fallback="sessions")

# PostgreSQL
POSTGRES_URI = config.get("POSTGRESQL", "POSTGRES_URI")
POSTGRES_DB = config.get("POSTGRESQL", "POSTGRES_DB")
POSTGRES_USER = config.get("POSTGRESQL", "POSTGRES_USER")
POSTGRES_PASSWORD = config.get("POSTGRESQL", "POSTGRES_PASSWORD")

# POSTGRESQL METADATA
# POSTGRES_URI = config.get("POSTGRESQL", "POSTGRES_URI")

# MILVUS_DB
# MILVUS_HOST = config.get("MILVUS_DB", "MILVUS_HOST")
# MILVUS_PORT = config.get("MILVUS_DB", "MILVUS_PORT")
# MILVUS_DB_INDEX = config.get("MILVUS_DB", "MILVUS_DB_INDEX")


class LOG:
    LOG_BASE_PATH = config.get("LOG", "LOG_BASE_PATH")
    FILE_NAME = os.path.join(LOG_BASE_PATH, config.get("LOG", "FILE_NAME"))
    LOG_HANDLERS = config.get("LOG", "LOG_HANDLERS").split(',')
    FILE_MAX_SIZE = config.get("LOG", "FILE_MAX_SIZE")
    FILE_BACKUP_COUNT = config.get("LOG", "FILE_BACKUP_COUNT")
    LOG_LEVEL = config.get("LOG", "LOG_LEVEL", fallback="INFO")


# class Agent:
#     CHATBOT_AGENT_ID = config.get("AGENT", "CHATBOT_AGENT_ID", fallback="agent_0")
#
#
# class EmbeddingConfig:
#     embedding_api_version = config.get("EMBEDDING", "EMBEDDING_API_VERSION", fallback="2023-05-15")
#     embedding_api_type = config.get("EMBEDDING", "EMBEDDING_API_TYPE", fallback="azure")
#     embedding_api_base = config.get("EMBEDDING", "EMBEDDING_API_BASE",
#                                     fallback="https://azr-oai-dai-kl-102.openai.azure.com/")
#     embedding_api_key = config.get("EMBEDDING", "EMBEDDING_API_KEY", fallback="2d990eb69065456795f663dedf3c60d8")
#     embedding_model_name = config.get("EMBEDDING", "EMBEDDING_MODEL_NAME", fallback="text-embedding-ada-002")
#
#
# class CompletionLLMConfig:
#     completion_api_version = config.get("LLM", "COMPLETION_API_VERSION", fallback="2023-05-15")
#     completion_api_type = config.get("LLM", "COMPLETION_API_TYPE", fallback="azure")
#     completion_api_base = config.get("LLM", "COMPLETION_API_BASE",
#                                      fallback="https://azr-oai-dai-kl-101.openai.azure.com/")
#     completion_api_key = config.get("LLM", "COMPLETION_API_KEY", fallback="87c45508cffa4aa992cdc81bd43b0879")
#     completion_model_name = config.get("LLM", "COMPLETION_MODEL_NAME", fallback="KL-POC-GPT4-32k")
#     completion_temperature = config.getint("LLM", "COMPLETION_TEMPERATURE", fallback=0)

# Git Configuration
GIT_PROVIDER = config.get("GIT", "GIT_PROVIDER", fallback="gitlab")

# GitLab Configuration
GITLAB_SERVER_URL = config.get("GITLAB", "GITLAB_SERVER_URL", fallback="https://gitlab.com")
GITLAB_API_VERSION = config.get("GITLAB", "GITLAB_API_VERSION", fallback="v4")
GITLAB_PROJECT_ID = config.get("GITLAB", "GITLAB_PROJECT_ID", fallback="12345")
GITLAB_ACCESS_TOKEN = config.get("GITLAB", "GITLAB_ACCESS_TOKEN", fallback="your_gitlab_token")

# GitHub Configuration
GITHUB_API_URL = config.get("GITHUB", "GITHUB_API_URL", fallback="https://api.github.com")
GITHUB_REPO = config.get("GITHUB", "GITHUB_REPO", fallback="project")
GITHUB_ACCESS_TOKEN = config.get("GITHUB", "GITHUB_ACCESS_TOKEN",
                                 fallback="")

# Chat configurations
LLM_PROVIDER = config.get("CHAT", "LLM_PROVIDER", fallback="anthropic")
LLM_API_KEY = config.get("CHAT", "LLM_API_KEY", fallback="")
LLM_MODEL = config.get("CHAT", "LLM_MODEL", fallback="claude-3-sonnet-20240229")
MLFLOW_TRACKING_URI = config.get("CHAT", "MLFLOW_TRACKING_URI", fallback="http://localhost:5080")
TEMPERATURE = config.getfloat("CHAT", "TEMPERATURE", fallback=0.7)

# Azure OpenAI specific settings
AZURE_API_VERSION = config.get("CHAT", "AZURE_API_VERSION", fallback="2024-02-15-preview")
AZURE_API_BASE = config.get("CHAT", "AZURE_API_BASE", fallback="")
AZURE_DEPLOYMENT_NAME = config.get("CHAT", "AZURE_DEPLOYMENT_NAME", fallback="")

# MLflow configurations
MLFLOW_ENABLE_AUTOLOG = config.getboolean("MLFLOW", "ENABLE_AUTOLOG", fallback=True)

CODING_TASK_NOTEBOOK = config.get("ASSESSMENT", "CODING_TASK_NOTEBOOK",
                                  fallback=os.path.join("assets", "responses"))
