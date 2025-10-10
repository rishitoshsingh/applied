import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from langgraph.graph import END, START, StateGraph

from categorizer_new.graph.consts import ORCHESTRATOR, TASK_CATEGORIZER, TASKS_SPLITTER
from categorizer_new.graph.nodes.conversation_splitter import conversation_splitter_node
from categorizer_new.graph.nodes.orchestrator import orchestrator_node
from categorizer_new.graph.nodes.task_categorizer import task_categorizer_node
from categorizer_new.graph.state import CategorizerState

categorizer_workflow = StateGraph(CategorizerState)
categorizer_workflow.add_node(TASKS_SPLITTER, conversation_splitter_node)
categorizer_workflow.add_node(TASK_CATEGORIZER, task_categorizer_node)
categorizer_workflow.add_node(ORCHESTRATOR, orchestrator_node)

categorizer_workflow.add_edge(START, TASKS_SPLITTER)
categorizer_workflow.add_edge(TASKS_SPLITTER, ORCHESTRATOR)
categorizer_workflow.add_conditional_edges(
    ORCHESTRATOR,
    lambda state: state["router_next_state"],
    {
        TASK_CATEGORIZER: TASK_CATEGORIZER,
        "end": END,
    }
)

categorizer_workflow.add_edge(TASK_CATEGORIZER, ORCHESTRATOR)


categorizer_graph = categorizer_workflow.compile()

if __name__ == "__main__":
    from IPython.display import Image, display

    img_data = categorizer_graph.get_graph().draw_mermaid_png()
    with open("categorizer_graph.png", "wb") as f:
        f.write(img_data)
