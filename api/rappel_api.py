from fastapi import FastAPI
from pydantic import BaseModel
from Core.Agents.agent_rappel import graph  
import uvicorn
app = FastAPI()

class RappelRequest(BaseModel):
    
    run: bool = True

@app.post("/rappels/start")
async def start_rappel_agent(request: RappelRequest):
    try:
        if request.run:
            result = graph.invoke({})
            return {"status": "success", "message": "Rappel terminé"}
        else:
            return {"status": "skipped", "message": "Exécution ignorée"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("api.rappel_api:app", host="127.0.0.1", port=8003, reload=True)