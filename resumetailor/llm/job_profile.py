from typing import Annotated
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from resumetailor.models import JobProfile
from resumetailor.llm.prompts import job_profile_prompts as prompts
from resumetailor.services.utils import model_to_str, str_to_model
from resumetailor.services.retry import RetryableChain

load_dotenv()


class JobState(MessagesState):
    job_description: Annotated[str, "The full job description text."]
    job_profile: Annotated[
        JobProfile | None, "The extracted information from the job description."
    ]
    editing_suggestions: Annotated[
        str | None, "User suggestions or comments for editing the job profile."
    ]
    done: Annotated[
        bool, "Flag indicating whether the job profile extraction is complete."
    ] = False


class JobProfileExtractor:
    _model_type = "LLM_MODEL_SUMMARY"

    def __init__(self):
        self._create_model()
        self._create_graph()

    def _create_model(self):
        self.model_job_profile = ChatOpenAI(
            model=os.getenv(self._model_type),
            use_responses_api=True,
        ).with_structured_output(JobProfile)

    def _create_graph(self):
        def extract_job_profile(state: JobState):
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts["extractor"]["system_message"]),
                    ("human", prompts["extractor"]["prompt"]),
                ]
            )
            chain = prompt | self.model_job_profile
            retryable_chain = RetryableChain(chain)
            response = retryable_chain.invoke(state)
            message = AIMessage(
                "Here is the extracted job profile:\n\n"
                f"```json\n{model_to_str(response)}\n```"
            )
            return {"job_profile": response, "messages": [message]}

        def edit_job_profile(state: JobState):
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts["editor"]["system_message"]),
                    MessagesPlaceholder("messages"),
                    ("human", prompts["editor"]["prompt"]),
                ]
            )
            chain = prompt | self.model_job_profile
            retryable_chain = RetryableChain(chain)
            response = retryable_chain.invoke(state)
            message = AIMessage(
                "Here is the extracted job profile:\n\n"
                f"```json\n{model_to_str(response)}\n```"
            )
            return {"job_profile": response, "messages": [message]}

        def human_node(state: JobState):
            result = interrupt(None)
            if result["edited_job_profile"] is None:
                return {
                    "editing_suggestions": result["editing_suggestions"],
                    "done": result["done"],
                }
            else:
                return {
                    "job_profile": result["edited_job_profile"],
                    "messages": [
                        {
                            "role": "user",
                            "content": f"I updated the job profile to better fit my needs. \n\n**Job Profile:** \n{model_to_str(result['edited_job_profile'])}",
                        }
                    ],
                    "editing_suggestions": result["editing_suggestions"],
                    "done": result["done"],
                }

        def editing_router(state: JobState):
            if not state["done"]:
                return "edit_job_profile"
            else:
                return END

        builder = StateGraph(JobState)
        builder.add_node("extract_job_profile", extract_job_profile)
        builder.add_node("edit_job_profile", edit_job_profile)
        builder.add_node("human_node", human_node)

        builder.add_edge(START, "extract_job_profile")
        builder.add_edge("extract_job_profile", "human_node")
        builder.add_conditional_edges("human_node", editing_router)

        checkpointer = MemorySaver()
        self.graph = builder.compile(checkpointer=checkpointer)

    def extract(self, job_description: str, thread_id: str) -> JobProfile:
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = JobState(job_description=job_description)
        result = self.graph.invoke(initial_state, config=config)
        return result["job_profile"]

    def edit(
        self,
        editing_suggestions: str,
        thread_id: str,
        edited_job_profile: JobProfile | None = None,
    ) -> JobProfile:
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "edited_job_profile": edited_job_profile,
                    "editing_suggestions": editing_suggestions,
                    "done": False,
                }
            ),
            config=config,
        )
        return result["job_profile"]

    def complete(
        self, thread_id: str, edited_job_profile: JobProfile | None = None
    ) -> JobProfile:
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "edited_job_profile": edited_job_profile,
                    "editing_suggestions": None,
                    "done": True,
                }
            ),
            config=config,
        )
        return result["job_profile"]
