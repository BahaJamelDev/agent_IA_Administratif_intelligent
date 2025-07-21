from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda as Runnable
from pydantic import BaseModel
from typing import Optional
from Core.tools.tools_vols import filter_flights

class FlightSearchState(BaseModel):
    destination: Optional[str] = None
    max_price: Optional[float] = None
    date: Optional[str] = None  # Format: "jj/mm/aaaa"
    result: Optional[str] = None

# 🔍 Noeud LangGraph pour exécuter la recherche
def search_node(state: FlightSearchState) -> FlightSearchState:
    result = filter_flights(state.destination, state.max_price, state.date)
    state.result = result
    return state

# 🔧 Construction du graphe
def build_flight_graph():
    graph = StateGraph(FlightSearchState)
    graph.add_node("search", Runnable(search_node))
    graph.set_entry_point("search")
    graph.set_finish_point("search")
    return graph.compile()

if __name__ == "__main__":
    graph_app = build_flight_graph()

    # Exemple d'entrée utilisateur
    user_state = FlightSearchState(
        destination="Paris",
        max_price=800,
        date="01/09/2025"
    )

    final_state = graph_app.invoke(user_state)
    print(final_state)
