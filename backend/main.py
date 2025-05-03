if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("dev-variables.env")

import multiprocessing
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from constants.configurations import FAST_SERVICE_PORT, SERVICE_HOST
from core.apis import router
from utils.logger_utility import logger
from exceptions.mcq import MCQException
from exceptions.handlers import mcq_exception_handler


class FastAPIServices:
    @staticmethod
    def fast_api():
        app = FastAPI()
        app.include_router(router)

        # Add exception handlers
        app.add_exception_handler(MCQException, mcq_exception_handler)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "DELETE", "PUT"],
            allow_headers=["*"],
        )

        try:
            uvicorn.run(app, host=SERVICE_HOST, port=int(FAST_SERVICE_PORT), log_level="debug")

        except Exception as ex:
            logger.exception(f"Unable to launch FAST API: {ex}")


if __name__ == "__main__":
    try:
        logger.info("FAST API services are running..")
        p1 = multiprocessing.Process(target=FastAPIServices().fast_api)
        p1.start()

    except Exception as e:
        logger.exception(f"Failed to deploy services:{e}")
