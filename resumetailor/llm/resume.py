# app/services/gpt_resume.py
import os
from typing import Literal, TypeVar, Generic, Annotated, TypedDict
from pydantic import BaseModel, create_model, Field
from dotenv import load_dotenv
from rich import print

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, Send
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, add_messages


from resumetailor.models import Resume, OutputResume, SectionType
from resumetailor.models.resume import (
    Degree,
    WorkPosition,
    Project,
    Achievement,
    Certification,
    SkillCategory,
    Publication,
)
from resumetailor.llm.prompts import resume_prompts as prompts
from resumetailor.services.utils import model_to_str

load_dotenv()


class ResumeState(TypedDict):
    """
    TypedDict to manage the state of the resume generation process.
    """

    # Required
    full_resume: Annotated[
        Resume, "The full non-refined resume provided by the candidate, required."
    ]
    task: Annotated[
        Literal["refine_with_job", "refine_without_job"],
        "The task of resume refinement to apply, either 'refine_with_job' or 'refine_without_job'.",
    ]
    # Conditional: If "refine_with_job"
    job_profile: Annotated[
        str | None,
        "The job profile to use as context for refining the resume as JSON string, if applicable.",
    ] = ""
    # Conditional: If "refine_without_job" (can be empty string)
    job_titles: Annotated[
        str | None,
        "A string with a list of job titles to adapt the resume to, if applicable.",
    ]
    focus_aspects: Annotated[
        str | None,
        "A string with a list of focus aspects to adapt the resume to, if applicable.",
    ]
    # filled by AI writers and editors
    education: Annotated[
        list[Degree] | None,
        "The refined education details of the candidate as JSON string.",
    ]
    work_experience: Annotated[
        list[WorkPosition] | None,
        "The refined work experience details of the candidate as JSON string.",
    ]
    projects: Annotated[
        list[Project] | None,
        "The refined projects details of the candidate as JSON string.",
    ]
    achievements: Annotated[
        list[Achievement] | None,
        "The refined achievements details of the candidate as JSON string.",
    ]
    certifications: Annotated[
        list[Certification] | None,
        "The refined certifications details of the candidate as JSON string.",
    ]
    additional_skills: Annotated[
        list[SkillCategory] | None,
        "The refined additional skills details of the candidate as JSON string.",
    ]
    publications: Annotated[
        list[Publication] | None,
        "The refined publications details of the candidate as JSON string.",
    ]
    done: Annotated[
        bool, "Indicates whether the resume refinement process is complete."
    ] = False
    edit: Annotated[
        bool, "Indicates whether the resume should be generated or edited."
    ] = False


T = TypeVar("T", bound=BaseModel)

# class Section(BaseModel, Generic[T]):
#     section_data: list[T]


class SectionState(TypedDict, Generic[T]):
    full_resume: str
    job_profile: str
    task: str
    editing_suggestions: str | None
    job_titles: str | None
    focus_aspects: str | None
    section_messages: Annotated[list[AnyMessage], add_messages]
    section_data: list[T] | None
    edit: bool


class ResumeWriter:
    model_type = "LLM_MODEL_RESUME"
    temperature = 0.4

    def __init__(self):
        self.sections = [
            "education",
            "work_experience",
            "projects",
            "achievements",
            "certifications",
            "additional_skills",
            "publications",
        ]
        self._create_model()
        self._create_graph()

    def generate(
        self,
        thread_id: str,
        resume: Resume,
        job_profile: str | None = None,
        job_titles: str | None = None,
        focus_aspects: str | None = None,
    ) -> Resume:
        """
        Generates a refined resume based on the provided full resume and either a job profile or a list of job titles/focus aspects.

        Args:
            thread_id (str): The thread ID for tracking the conversation.
            resume (Resume): The initial resume to refine.
            job_profile (str | None): The job profile to adapt the resume to, if applicable.
            job_titles (str | None): A string with a list of job titles to adapt the resume to, if applicable.
            focus_aspects (str | None): A string with a list of focus aspects to adapt the resume to, if applicable.

        Returns:
            Resume: The refined resume in structured format.
        """
        if job_profile is None:
            return self._generate_without_job(
                thread_id, resume, job_titles or "", focus_aspects or ""
            )
        else:
            return self._generate_with_job(thread_id, resume, job_profile)

    def _generate_with_job(self, thread_id: str, resume: Resume, job_profile: str):
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = ResumeState(
            full_resume=resume,
            task="refine_with_job",
            job_profile=job_profile,
            done=False,
            edit=False,
        )
        result = self.graph.invoke(initial_state, config=config)
        return result["__interrupt__"][0].value["refined_resume"]

    def _generate_without_job(
        self, thread_id: str, resume: Resume, job_titles: str, focus_aspects: str
    ):
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = ResumeState(
            full_resume=resume,
            task="refine_without_job",
            job_titles=job_titles,
            focus_aspects=focus_aspects,
            done=False,
            edit=False,
        )
        result = self.graph.invoke(initial_state, config=config)
        return result["__interrupt__"][0].value["refined_resume"]

    def edit_section(
        self,
        thread_id: str,
        section_key: str,
        editing_suggestions: str,
        user_edited_section: SectionType | None = None,
    ) -> SectionType:
        """
        Edits a specific section of the resume based on user input and suggestions.

        Args:
            thread_id (str): The thread ID for tracking the conversation.
            section_key (str): The key of the section to edit (e.g., 'education', 'work_experience').
            suggestions (str): Suggestions for editing the section.
            user_edited_section (SectionType): The user's edited version of the section.

        Returns:
            SectionType: The updated section data.
        """

        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "section_key": section_key,
                    "editing_suggestions": editing_suggestions,
                    "user_edited_section": user_edited_section,
                    "done": False,
                }
            ),
            config=config,
        )
        return result[section_key]

    def complete(
        self, thread_id: str, user_edited_resume: Resume | None = None
    ) -> OutputResume:
        """
        Completes the resume refinement process and returns the final refined resume.

        Args:
            thread_id (str): The thread ID for tracking the conversation.
            user_edited_resume (dict | None): The user's edited version of the resume, if any.

        Returns:
            Resume: The final refined resume in structured format.
        """
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(
            Command(
                resume={
                    "done": True,
                }
            ),
            config=config,
        )
        resume = Resume(**result) if user_edited_resume is None else user_edited_resume
        return self._output_compiler(resume)

    def _create_model(self):
        self.model = ChatOpenAI(
            model=os.getenv(self.model_type),
            temperature=self.temperature,
            use_responses_api=True,
        )

    def _create_graph(self):
        def start_router(state: ResumeState):
            sections_to_write = []
            for section in self.sections:
                if getattr(state["full_resume"], section) is not None:
                    sections_to_write.append(f"{section}_writer")
            return sections_to_write

        def human_node(state: ResumeState):
            result = interrupt({"refined_resume": Resume(**state)})
            if result["done"]:
                return Command(goto=END)
            elif result["user_edited_section"] is None:
                return Send(
                    node=f"{result['section_key']}_writer",
                    arg={
                        "editing_suggestions": result["editing_suggestions"],
                        "edit": True,
                    },
                )
            else:
                section_name = result["section_key"].replace("_", " ")
                user_message = HumanMessage(
                    f"I updated the {section_name} section to better fit my needs.\n\n"
                    f"**{section_name.capitalize()}:**\n"
                    f"```json\n{model_to_str(result['user_edited_section'])}\n```"
                )
                return Send(
                    node=f"{result['section_key']}_writer",
                    arg={
                        "section_messages": [user_message],
                        "editing_suggestions": result["editing_suggestions"],
                        "edit": True,
                    },
                )

        def end_router(state: ResumeState):
            if not state["done"]:
                return Command(goto="human_node")
            else:
                return Command(goto=END)

        builder = StateGraph(ResumeState)

        builder.add_node(
            "education_writer", self._create_section_module("education", Degree)
        )
        builder.add_node(
            "work_experience_writer",
            self._create_section_module("work_experience", WorkPosition),
        )
        builder.add_node(
            "projects_writer", self._create_section_module("projects", Project)
        )
        builder.add_node(
            "achievements_writer",
            self._create_section_module("achievements", Achievement),
        )
        builder.add_node(
            "certifications_writer",
            self._create_section_module("certifications", Certification),
        )
        builder.add_node(
            "additional_skills_writer",
            self._create_section_module("additional_skills", SkillCategory),
        )
        builder.add_node(
            "publications_writer",
            self._create_section_module("publications", Publication),
        )
        builder.add_node("human_node", human_node)
        builder.add_node("end_router", end_router)

        # Edges
        builder.add_conditional_edges(START, start_router)
        builder.add_edge("education_writer", "end_router")
        builder.add_edge("work_experience_writer", "end_router")
        builder.add_edge("projects_writer", "end_router")
        builder.add_edge("achievements_writer", "end_router")
        builder.add_edge("certifications_writer", "end_router")
        builder.add_edge("additional_skills_writer", "end_router")
        builder.add_edge("publications_writer", "end_router")

        checkpointer = MemorySaver()
        self.graph = builder.compile(checkpointer=checkpointer)

    def _create_section_module(self, section_key: str, SectionModel: type[T]):
        section_class_name = section_key.replace("_", " ").capitalize().replace(" ", "")
        ThisSection = create_model(
            f"{section_class_name}Section",
            section_data=Annotated[
                list[SectionModel],
                Field(
                    description="The refined section data of the candidate, extracted from JSON."
                ),
            ],
            explanation=Annotated[
                str,
                Field(
                    description="A detailed explanation of the changes made and the reasoning behind it."
                ),
            ],
        )
        ThisSectionState = type(
            f"{section_key.capitalize()}SectionState",
            (SectionState,),
            {"T": SectionModel},
        )

        def writer_node(state: ThisSectionState):
            """Writes a single section of the resume based on the provided data."""
            system_message = prompts["writer"][state["task"]]["system_message"]
            section_prompt = prompts["writer"][state["task"]][section_key]
            prompt = ChatPromptTemplate.from_messages(
                [("system", system_message), ("human", section_prompt)]
            )
            chain = prompt | self.model.with_structured_output(ThisSection)
            additional_data = {
                "section_name": section_key,
                "candidate_data": "\n".join(
                    [
                        model_to_str(entry)
                        for entry in getattr(state["full_resume"], section_key)
                    ]
                ),
            }
            result = chain.invoke({**state, **additional_data})
            message = AIMessage(
                f"```json\n{result.section_data}\n```\n\n**Explanation of Changes:**\n{result.explanation}"
            )
            return {"section_messages": [message], "section_data": result.section_data}

        def editor_node(state: ThisSectionState):
            """Edits a single section, based on user edits and suggestions."""
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts["section_editor"]["system_message"]),
                    MessagesPlaceholder("section_messages"),
                    ("human", prompts["section_editor"]["prompt"]),
                ]
            )
            chain = prompt | self.model.with_structured_output(ThisSection)
            additional_data = {
                "section_name": section_key,
            }
            result = chain.invoke({**state, **additional_data})
            message = AIMessage(
                f"```json\n{result.section_data}\n```\n\n**Explanation of Changes:**\n{result.explanation}"
            )
            return {"section_messages": [message], "section_data": result.section_data}

        def route_to_parent(state: ThisSectionState):
            return Command(
                graph=Command.PARENT,
                goto="human_node",
                update={section_key: state["section_data"]},
            )

        builder = StateGraph(ThisSectionState)
        builder.add_node("writer_node", writer_node)
        builder.add_node("editor_node", editor_node)
        builder.add_node("route_to_parent", route_to_parent)

        builder.add_conditional_edges(
            START, lambda s: "editor_node" if s["edit"] else "writer_node"
        )
        builder.add_edge("writer_node", "route_to_parent")
        builder.add_edge("editor_node", "route_to_parent")

        graph = builder.compile(checkpointer=True)

        return graph

    def _output_compiler(self, resume: Resume) -> OutputResume:
        system_message = prompts["compiler"]["system_message"]
        prompt_template = prompts["compiler"]["prompt_template"]
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", prompt_template)]
        )
        chain = prompt | self.model.with_structured_output(OutputResume)
        output_resume = chain.invoke({"resume": resume})
        return output_resume

    def _create_resume_editor(self):
        # TODO: create the editor for the whole resume
        pass


# class ResumeAgentState(AgentState):
#     job_profile: Optional[str] = Field(None, description="The job profile to adapt the resume to.")
#     full_resume: Optional[str] = Field(None, description="The full resume in JSON format.")
#     adapted_resume: Optional[Resume] = Field(None, description="The adapted resume in JSON format.")
#     structured_response: Optional[StructuredResponse] = Field(None)

# state = ResumeAgentState()
# state = AgentState()
