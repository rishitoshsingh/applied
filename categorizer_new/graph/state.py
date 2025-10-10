from operator import add
from typing import Annotated, Sequence, TypedDict, Union

from .chains.conversation_splitting import TasksConversation
from .chains.task_categorizing import TaskCategoryResponse


class CategorizerState(TypedDict):
    original_conversation: Sequence[dict[str, str]]
    tasks_conversation: TasksConversation
    task_categorized: Annotated[int, add]
    router_next_state: Union[str, None]
    tasks_category: Annotated[Sequence[TaskCategoryResponse], add]
