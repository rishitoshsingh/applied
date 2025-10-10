from typing import Dict

from categorizer_new.graph.chains.conversation_splitting import (
    conversation_splitting_chain,
)
from categorizer_new.graph.state import CategorizerState


def conversation_splitter_node(state: CategorizerState) -> None:
    # print("~" * 5, " conversation_splitter_node ", "~" * 5)
    result = conversation_splitting_chain.invoke({"original_conversation": state["original_conversation"]})
    return {"tasks_conversation": result}
