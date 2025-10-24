# Code adapted from:
# https://github.com/junfanz1/Cognito-LangGraph-RAG-Chatbot/blob/main/graph/chains/answer_grader.py
# Author: Junfan Zhang (https://github.com/junfanz1)
# License: Apache License 2.0
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.runnables import RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

llm = None
temperature = float(os.getenv("temperature"))
if temperature is None:
    temperature = 0.1
if os.getenv("model_name").startswith("gemini"):
    llm = ChatGoogleGenerativeAI(
            model=os.getenv("model_name"),
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            rate_limiter=rate_limiter,
        )
elif os.getenv("model_name").startswith("gpt"):
    llm = ChatOpenAI(
            model_name=os.getenv("model_name"),
            temperature=temperature,
            max_retries=2,
            rate_limiter=rate_limiter,
        )
elif os.getenv("model_name").startswith("claude"):
    llm = ChatAnthropic(
            model_name=os.getenv("model_name"),
            temperature=temperature,
            max_retries=2,
            rate_limiter=rate_limiter,
        )

class TaskCategoryResponse(BaseModel):
    category: str = Field(..., description="Category of the task, either 'procedural', or 'declarative''")
    reasoning: str = Field(..., description="Your reasoning for the categorization")

categorizer_model = llm.with_structured_output(TaskCategoryResponse)


tasks_type_str = ""
if os.getenv("traj_type") == "flight":
    tasks_type_str = "BOOK, MODIFY, CANCEL"
elif os.getenv("traj_type") == "retail":
    tasks_type_str = "CANCEL_ORDER, MODIFY_ORDER, RETURN_ORDER, EXCHANGE_ORDER, MODIFY_ADDRESS"


system = f"""
You are an expert conversation annotator.
You will receive a JSON object containing:
	•	The intent of the conversation segment (one of {tasks_type_str})
	•	The conversation_segment, which includes the dialogue between the user and the agent.

Your goal is to analyze the conversation and determine whether it is procedural, declarative.

Rules:
	1.	When a conversation is a procedural:
        * When user is providing step-by-step instructions to the assistant, like do this, try this and the agent follows without reasoning or decision-making.
        * When the user is asking the agent to perform a specific task or action, and the agent is executing it without reasoning or decision-making.
    2.	When a conversation is declarative:
        * When the user is seeking information, explanations, or understanding, and the agent is providing reasoning, explanations, or making decisions.
        * When the user is sharing information or context, and the agent is interpreting, reasoning, or making decisions based on that information.
"""

# Rules:
# 1. Procedural:
#     * User provides explicit instructions or a step-by-step procedure for the agent to follow.
#     * Focus is on how to do something, not on what outcome the user wants.
# 2. Declarative:
#     * User requests an action, expresses a desire, or shares information without specifying instructions.
#     * User seeks explanations, information, or understanding.
#     * Agent may reason or make decisions to fulfill the user’s request.
# Tip: Requests for actions without step-by-step instructions are declarative.


user = """
Analyze the following intent-based conversation and classify it as procedural, declarative, according to the rules provided.
Conversation intent: {intent}
Conversation segment: \n {conversation_segment}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", user),
    ]
)



task_categorizing_chain: RunnableSequence = prompt | categorizer_model
