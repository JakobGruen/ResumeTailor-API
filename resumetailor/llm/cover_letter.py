from typing import Annotated, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
import os
from dotenv import load_dotenv

load_dotenv()

from resumetailor.models import CoverLetter
from resumetailor.llm.prompts import cover_letter_prompts as prompts
from resumetailor.services.utils import model_to_str
import uuid


class CoverLetterState(MessagesState):
    job_profile: Annotated[str, "The AI-extracted job profile as JSON string."]
    candidate_resume: Annotated[str, "The candidate's refined resume as JSON string."]
    job_description: Annotated[
        str | None, "The original job description text, for style/tone only."
    ]
    editing_suggestions: Annotated[
        str | None, "User suggestions or comments for editing the cover letter."
    ]
    cover_letter: Annotated[
        CoverLetter | None, "The generated or edited cover letter as JSON."
    ]
    done: Annotated[
        bool,
        "Flag indicating whether the cover letter generation or editing is complete.",
    ]


class CoverLetterWriter:
    _model_type = "LLM_MODEL_COVER_LETTER"
    _temperature = 0.4

    def __init__(self):
        self._create_model()
        self._create_graph()

    def generate(
        self,
        thread_id: str,
        job_profile: str,
        candidate_resume: str,
        job_description: str | None = None,
    ) -> CoverLetter:
        """
        Generate a cover letter based on the provided job profile, candidate resume, and optional job description.
        Args:
            thread_id (str): Unique identifier for the conversation or session.
            job_profile (str): Description of the job or position being applied for.
            candidate_resume (str): The candidate's resume or relevant experience.
            job_description (str, optional): The job description provided by the employer. Defaults to None.
        Returns:
            CoverLetter: The generated cover letter object.
        """
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = CoverLetterState(
            job_profile=job_profile,
            candidate_resume=candidate_resume,
            job_description=job_description,
            done=False,
        )
        result = self.graph.invoke(initial_state, config=config)
        return result["cover_letter"]

    def edit(
        self,
        thread_id: str,
        editing_suggestions: str,
        user_edited_cover_letter: str | None = None,
    ) -> CoverLetter:
        """
        Edit an existing cover letter using user-provided suggestions and/or a user-edited version of the cover letter.
        Args:
            thread_id (str): Unique identifier for the conversation or session.
            editing_suggestions (str): Suggestions or feedback for editing the cover letter.
            user_edited_cover_letter (str, optional): The cover letter text edited by the user. Defaults to None.
        Returns:
            CoverLetter: The updated cover letter object after applying edits.
        """
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "user_edited_cover_letter": user_edited_cover_letter,
                    "editing_suggestions": editing_suggestions,
                    "done": False,
                }
            ),
            config=config,
        )
        return result["cover_letter"]

    def complete(
        self, thread_id: str, user_edited_cover_letter: CoverLetter | None = None
    ) -> CoverLetter:
        """
        Complete the cover letter generation or editing process, allowing the user to finalize their edits.
        Args:
            thread_id (str): Unique identifier for the conversation or session.
            user_edited_cover_letter (CoverLetter | None): The user's final edited version of the cover letter. Defaults to None.
        Returns:
            CoverLetter: The finalized cover letter object.
        """
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "user_edited_cover_letter": user_edited_cover_letter,
                    "done": True,
                }
            ),
            config=config,
        )
        return result["cover_letter"]

    def _create_model(self):
        self.model = ChatOpenAI(
            model=os.getenv(self._model_type),
            temperature=self._temperature,
            use_responses_api=True,
        )

    def _create_graph(self):
        def writer_node(state: CoverLetterState):
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts["writer"]["system_message"]),
                    ("human", prompts["writer"]["prompt"]),
                ]
            )
            chain = prompt | self.model
            result = chain.invoke(state)
            cover_letter = self.model.with_structured_output(CoverLetter).invoke(
                [result]
            )
            return {
                "messages": [result],
                "cover_letter": cover_letter,
            }

        def editor_node(state: CoverLetterState):
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts["editor"]["system_message"]),
                    MessagesPlaceholder("messages"),
                    ("human", prompts["editor"]["prompt"]),
                ]
            )
            chain = prompt | self.model
            result = chain.invoke(state)
            cover_letter = self.model.with_structured_output(CoverLetter).invoke(
                [result]
            )
            return {
                "messages": [result],
                "cover_letter": cover_letter,
            }

        def human_node(state: CoverLetterState):
            result = interrupt(None)
            if result["done"]:
                return {"done": True}
            elif result["user_edited_cover_letter"] is None:
                return {
                    "editing_suggestions": result["editing_suggestions"],
                }
            else:
                user_message = HumanMessage(
                    f"I updated the cover letter section to better fit my needs.\n\n"
                    f"**Cover Letter:**\n"
                    f"```json\n{model_to_str(result['user_edited_section'])}\n```"
                )
                return {
                    "messages": [user_message],
                    "editing_suggestions": result["editing_suggestions"],
                }

        def editing_router(state: CoverLetterState):
            if not state["done"]:
                return "editor_node"
            else:
                return END

        builder = StateGraph(CoverLetterState)
        builder.add_node("writer_node", writer_node)
        builder.add_node("editor_node", editor_node)
        builder.add_node("human_node", human_node)

        builder.add_edge(START, "writer_node")
        builder.add_edge("writer_node", "human_node")
        builder.add_edge("editor_node", "human_node")
        builder.add_conditional_edges("human_node", editing_router)

        checkpointer = MemorySaver()
        self.graph = builder.compile(checkpointer=checkpointer)
