from typing import Dict

from categorizer_new.graph.consts import TASK_CATEGORIZER
from categorizer_new.graph.state import CategorizerState


def orchestrator_node(state: CategorizerState) -> Dict[str, str]:
    # print("~" * 5, " orchestrator_node ", "~" * 5)
    if state["task_categorized"] == len(state["tasks_conversation"].items):
        return {
            "router_next_state": "end"
        }
    else:
        return {
            "router_next_state": TASK_CATEGORIZER
        }
