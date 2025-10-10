# Code adapted from:
# https://github.com/junfanz1/Cognito-LangGraph-RAG-Chatbot/blob/main/graph/chains/answer_grader.py
# Author: Junfan Zhang (https://github.com/junfanz1)
# License: Apache License 2.0


import os
from typing import Dict, List, Sequence

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
if os.getenv("model_name") == "gemini-2.0-flash":    
    llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            rate_limiter=rate_limiter,
        )
elif os.getenv("model_name") == "gpt-4o":
    llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.1,
            max_retries=2,
            rate_limiter=rate_limiter,
        )

tasks_type_str = ""
if os.getenv("traj_type") == "flight":
    tasks_type_str = "BOOK, MODIFY, CANCEL"
elif os.getenv("traj_type") == "retail":
    tasks_type_str = "CANCEL_ORDER, MODIFY_ORDER, RETURN_ORDER, EXCHANGE_ORDER, MODIFY_ADDRESS"

class UserRequest(BaseModel):
    intent: str = Field(description=f"Intent of the user request, one of {tasks_type_str}")
    conversation_segment: str = Field(description="""The conversation segment for this request, including both user and agent messages.""")
 

class TasksConversation(BaseModel):
    items: List[UserRequest] = Field(description="A list of user requests extracted from the conversation")

splitter_model = llm.with_structured_output(TasksConversation)
# splitter_model = llm.with_structured_output(schema=TasksConversation, method="json_mode")

system = f"""
    You are an expert conversation analyst. Your task is to segment a dialogue between a customer and a service agent into separate requests, based on user intent. Each request corresponds to one of the following intent types: {tasks_type_str}.

    The conversation may include multiple intents in sequence. You must detect when a new request begins and split the dialogue accordingly.

    Guidelines:
        1.	Each segment must include all the user and agent messages relevant to that intent.
        2.	Do not mix messages from different intents in the same segment.
        3.	Preserve message order and text as-is inside each segment.
        4.	If small talk or unrelated dialogue occurs, include it in the segment where it naturally fits.
    """

user = f"""
Below is a conversation between a customer and a service agent.
Your task is to identify and separate all distinct user requests from the conversation.
Each request should be labeled with one of the following intent types: {tasks_type_str}.

For each intent, extract the full part of the dialogue (both user and agent messages) that belong to that request.
If the conversation contains multiple requests, split it into multiple intent segments in chronological order.
Return the output strictly in the JSON format shown in the instructions.

Conversation:"""+"""
{original_conversation}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", user),
    ]
)

conversation_splitting_chain: RunnableSequence = prompt | splitter_model
