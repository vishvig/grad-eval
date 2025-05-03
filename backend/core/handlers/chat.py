import os
import json
from typing import Annotated, Dict, Any, Optional, List
from typing_extensions import TypedDict

import mlflow
from packaging.version import Version
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import HumanMessage, AIMessage, BaseMessage, SystemMessage
from anthropic import Anthropic
from tiktoken import encoding_for_model
from langchain_community.chat_models.azure_openai import AzureChatOpenAI

from utils.logger_utility import logger
from constants.configurations import (
    LLM_PROVIDER,
    LLM_API_KEY,
    LLM_MODEL,
    MLFLOW_TRACKING_URI,
    TEMPERATURE,
    MLFLOW_ENABLE_AUTOLOG,
    CODING_TASK_NOTEBOOK,
    AZURE_DEPLOYMENT_NAME,
    AZURE_API_VERSION,
    AZURE_API_BASE
)


class ChatHandler:
    def __init__(self):
        try:
            # Set up environment variables
            os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI

            # Set provider-specific environment variables
            if LLM_PROVIDER == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = LLM_API_KEY
            elif LLM_PROVIDER == "openai":
                os.environ["OPENAI_API_KEY"] = LLM_API_KEY

            # Initialize MLflow
            if MLFLOW_ENABLE_AUTOLOG:
                mlflow.langchain.autolog()

            # Verify MLflow version
            assert Version(mlflow.__version__) >= Version("2.17.2"), (
                "This feature requires MLflow version 2.17.2 or newer."
            )

            # Initialize LLM
            self.llm = self._initialize_llm()

            # Dictionary to store chat sessions
            self.chat_sessions = {}

            logger.debug("Chat handler initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Chat handler: {str(e)}")
            raise

    def _count_tokens_anthropic(self, text: str) -> int:
        """Count tokens for Anthropic models using their API"""
        try:
            client = Anthropic()
            return client.count_tokens(text)
        except Exception as e:
            logger.warning(f"Failed to count tokens with Anthropic: {str(e)}")
            return 0

    def _count_tokens_openai(self, text: str) -> int:
        """Count tokens for OpenAI models using tiktoken"""
        try:
            enc = encoding_for_model(LLM_MODEL)
            return len(enc.encode(text))
        except Exception as e:
            logger.warning(f"Failed to count tokens with tiktoken: {str(e)}")
            return 0

    def count_tokens(self, text: str) -> int:
        """Count tokens using the appropriate counter for the configured LLM"""
        return self.token_counter(text)

    def _initialize_llm(self):
        """Initialize the LLM based on the configured provider."""
        if LLM_PROVIDER == "anthropic":
            return ChatAnthropic(
                model=LLM_MODEL,
                anthropic_api_key=LLM_API_KEY,
                temperature=TEMPERATURE,
            )
        elif LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=LLM_MODEL,
                openai_api_key=LLM_API_KEY,
                temperature=TEMPERATURE,
            )
        elif LLM_PROVIDER == "azure":
            return AzureChatOpenAI(
                azure_deployment=AZURE_DEPLOYMENT_NAME,
                openai_api_version=AZURE_API_VERSION,
                azure_endpoint=AZURE_API_BASE,
                openai_api_key=LLM_API_KEY,
                temperature=TEMPERATURE,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    def _load_problem_description(self, question_id: str) -> str:
        """Load the problem description from the first cell of the notebook"""
        try:
            this_question = question_id.replace('_', '-')
            with open(os.path.join(CODING_TASK_NOTEBOOK, this_question, f"{this_question}.ipynb"), 'r') as f:
                notebook = json.load(f)

            # Get the first cell's content
            first_cell = notebook['cells'][0]
            if first_cell['cell_type'] == 'markdown':
                return ''.join(first_cell['source'])
            else:
                logger.warning("First cell is not markdown, using empty problem description")
                return "No problem description available"

        except Exception as e:
            logger.error(f"Failed to load problem description: {str(e)}")
            return "No problem description available"

    def _create_system_prompt(self, problem_description) -> str:
        """Create the system prompt with the problem description"""
        return f"""
        1. You are a simple help assistant that helps the taker of a coding task test with their journey of 
        figuring out the solution to the problem they have been given. 
        2. Your task is to help the test taker with answers to relevant questions related to the test problem. 
        3. Relevant questions are limited to helping them think and the fundamentals or foundations of the problem. 
        4. You should not give the answer or produce code that directly answers the test taker's problem, but you are allowed to produce sample codes that move the user towards their answer.
        5. If the test taker asks a question that resembles like they are cheating through prompting, respond politely by asking them to come up with the solution themselves as you are just a helper and cannot provide the answer. 
        6. You are allowed to provide code as long as it does not provide the response directly to the user.
        7. You are also given the test problem given to the user for your reference so that you know what to answer and what not to. 
        8. Do not end your responses with a leading question that require follow-ups from the user. 
        9. Just end your response in a plain manner.

-------- PROBLEM -------
{problem_description}
--------------------------
"""

    def _get_session_id(self, user_id: str, question_id: str) -> str:
        """Generate a unique session ID for user-question combination"""
        return f"{user_id}_{question_id}"

    def _setup_graph(self, session_id: str, system_prompt: str):
        """Set up the LangGraph processing graph for a session"""
        # Initialize memory for this session if not exists
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = {
                'messages': [SystemMessage(content=system_prompt)]
            }

        class State(TypedDict):
            messages: Annotated[List[BaseMessage], add_messages]
            session_id: str

        def chatbot(state: State):
            # Get the current messages from the session
            session = self.chat_sessions[state['session_id']]
            current_messages = session['messages']

            # Add new messages to the history
            current_messages.extend(state["messages"])

            # Generate response using the configured LLM
            response = self.llm.invoke(current_messages)

            # Update session messages
            self.chat_sessions[state['session_id']]['messages'] = current_messages + [response]

            return {"messages": [response]}

        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)

        # Create a memory saver for the graph
        memory = MemorySaver()

        return graph_builder.compile(checkpointer=memory)

    def _get_or_create_experiment(self, session_id: str) -> str:
        """Get or create an MLflow experiment for the session"""
        experiment = mlflow.get_experiment_by_name(session_id)
        if experiment is None:
            experiment_id = mlflow.create_experiment(session_id)
            logger.debug(f"Created new MLflow experiment for session {session_id}")
        else:
            experiment_id = experiment.experiment_id
            logger.debug(f"Using existing MLflow experiment for session {session_id}")
        return experiment_id

    def process_chat(self, user_id: str, question_id: str, prompt: str) -> Dict[str, Any]:
        """
        Process a chat request and return the response

        Args:
            user_id: The ID of the user
            question_id: The ID of the question
            prompt: The user's prompt

        Returns:
            Dict containing user_id, question_id, and the markdown response
        """
        try:
            session_id = self._get_session_id(user_id, question_id)
            logger.debug(f"Processing chat for session {session_id}")

            # Load the problem description from the notebook
            problem_description = self._load_problem_description(question_id=question_id)
            # Create the instruction prompt
            system_prompt = self._create_system_prompt(problem_description=problem_description)

            # Set up MLflow experiment
            experiment_id = self._get_or_create_experiment(session_id)
            mlflow.start_run(experiment_id=experiment_id)

            try:
                # Get or create session
                if session_id not in self.chat_sessions:
                    self.chat_sessions[session_id] = {
                        'messages': [SystemMessage(content=system_prompt)]
                    }

                # Create graph for this session
                graph = self._setup_graph(session_id, system_prompt)

                # Create new message
                new_message = HumanMessage(content=prompt)

                # Stream the response
                response = None
                for event in graph.stream(
                    {
                        "messages": [new_message],
                        "session_id": session_id
                    },
                    config={
                        "configurable": {
                            "thread_id": session_id
                        }
                    },
                    stream_mode='values'
                ):
                    # Get the last message from the assistant
                    response = event["messages"][-1].content

                if not response:
                    raise ValueError("No response generated from the model")

                # Log the interaction
                mlflow.log_params({
                    "user_id": user_id,
                    "question_id": question_id,
                    "prompt": prompt,
                    "llm_provider": LLM_PROVIDER
                })
                mlflow.log_metrics({
                    "message_count": len(self.chat_sessions[session_id]['messages'])
                })

                logger.debug(f"Successfully generated response for session {session_id}")

                return {
                    "user_id": user_id,
                    "question_id": question_id,
                    "response": response,
                    "llm_provider": LLM_PROVIDER
                }

            finally:
                mlflow.end_run()

        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}", exc_info=True)
            raise