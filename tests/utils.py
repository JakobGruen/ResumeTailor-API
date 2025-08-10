# tests/utils.py
from openai import OpenAI
from typing import TypedDict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import os
import dotenv

dotenv.load_dotenv()


class AspectScore(BaseModel):
    name: str = Field(
        description="The name of the aspect being evaluated, such as 'Overall Quality', 'Faithfulness', etc."
    )
    score: int = Field(
        description="A score for the aspect, ranging from 0 to 100, where 0 is the worst and 100 is the best."
    )


class Score(BaseModel):
    aspect_scores: list[AspectScore] = Field(
        description="A list of aspect scores, each containing the name of the aspect and its score."
    )
    score: int = Field(
        description="A single score from 0 to 100 with 0 being the worst and 100 being the best."
    )


def score_content(system_message: str, prompt: str, **kwargs) -> Score:
    """
    Evaluates the given prompt using a grading LLM and extracts an integer score between 0 and 100.
    Args:
        system_message (str): The system message to provide context or instructions to the grading LLM.
        prompt (str): The prompt or content to be evaluated by the grading LLM.
        **kwargs: Additional keyword arguments to be passed to the chain invocation.
    Returns:
        Score: A Score object containing the aspect scores and the overall score.
    Raises:
        Any exception raised by the underlying LLM or chain invocation.
    """

    model_grading = ChatOpenAI(
        model=os.environ.get("LLM_MODEL_GRADING"),
        use_responses_api=True,
    )
    model_extract = ChatOpenAI(
        model=os.environ.get("LLM_MODEL_GRADING"),
        use_responses_api=True,
    ).with_structured_output(Score)
    grading_messages = ChatPromptTemplate.from_messages(
        [("system", system_message), ("human", prompt)]
    )
    extraction_messages = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert evaluator. Your task is to extract a single integer score and aspect scores from a grading review. "
                "The overall score must be between 0 and 100, where 0 is the worst and 100 is the best. "
                "Additionally, extract scores for each aspect mentioned in the review as a dictionary, where keys are aspect names and values are their respective scores (also 0-100). "
                "Read the following grading review carefully and return only the overall score and the aspect scores as a dictionary. "
                "Do not include any explanation or additional text.",
            ),
            (
                "human",
                "Grading review:\n{graded_output}\n\n"
                "Extract and return the overall score (0-100) as an integer, and a dictionary of aspect scores (aspect: score).",
            ),
        ]
    )
    grading_chain = grading_messages | model_grading
    extraction_chain = extraction_messages | model_extract
    grading_output = grading_chain.invoke(kwargs)
    score = extraction_chain.invoke({"graded_output": grading_output.content})
    return score
