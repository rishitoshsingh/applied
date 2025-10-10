from typing import Dict

from categorizer_new.graph.chains.task_categorizing import task_categorizing_chain
from categorizer_new.graph.state import CategorizerState


def task_categorizer_node(state: CategorizerState) -> None:
    # print("~" * 5, " task_categorizer_node ", "~" * 5)
    result = task_categorizing_chain.invoke({
        "conversation_segment": state["tasks_conversation"].items[state["task_categorized"]].conversation_segment,
        "intent": state["tasks_conversation"].items[state["task_categorized"]].intent,
        })
    return {"task_categorized": 1, "tasks_category": [result]}
