from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Core.Agents.agent_vol import build_flight_graph, FlightSearchState
import uvicorn

app = FastAPI()

# Schéma d'entrée pour FastAPI (même que FlightSearchState mais en BaseModel)
class VolsRequest(BaseModel):
    destination: Optional[str] = None
    max_price: Optional[float] = None
    date: Optional[str] = None  

# Construire et compiler le graphe une fois au démarrage
graph_app = build_flight_graph()

@app.post("/vols/start")
async def start_vols_agent(request: VolsRequest):
    user_state = FlightSearchState(
        destination=request.destination,
        max_price=request.max_price,
        date=request.date
    )
    try:
        # 🛠️ Cast le dictionnaire en FlightSearchState
        final_state = FlightSearchState(**graph_app.invoke(user_state))
        return {
            "status": "success",
            "destination": final_state.destination,
            "max_price": final_state.max_price,
            "date": final_state.date,
            "result": final_state.result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run("api.vols_api:app", host="127.0.0.1", port=8001, reload=True)
