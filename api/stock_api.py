from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Core.Agents.agent_stock import workflow
import uvicorn

app = FastAPI()

# Schéma pour recevoir l'input utilisateur
class StockRequest(BaseModel):
    input: str

@app.post("/stock/start")
async def start_stock_agent(request: StockRequest):
    try:
        result = workflow.invoke({"input": request.input})
        return {
            "status": "success",
            "question": request.input,
            "response": result["output"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run("api.stock_api:app", host="127.0.0.1", port=8002, reload=True)