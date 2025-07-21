from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn
import httpx
import json
import logging
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("Clé API Groq non trouvée")
    raise ValueError("Clé API Groq non trouvée")

# URLs des agents (à configurer dans .env ou laisser valeurs par défaut)
AGENT_URLS = {
    "vols": os.getenv("AGENT_VOLS_URL", "http://localhost:8001/vols/start"),
    "stock": os.getenv("AGENT_STOCK_URL", "http://localhost:8002/stock/start"),
    "rappels": os.getenv("AGENT_RAPPELS_URL", "http://localhost:8003/rappels/start")
}

# Initialisation du client Groq
groq_client = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0.2
)

app = FastAPI()

class UserInput(BaseModel):
    message: str

TIMEOUT = 30.0  # timeout pour les requêtes HTTP

@app.post("/agent-maitre")
async def agent_maitre(user_input: UserInput):
    message = user_input.message
    logger.info(f"Requête reçue: {message}")

    system_prompt = """
Tu es un routeur intelligent d'agents IA. À partir du message utilisateur, tu dois :
1. Identifier quel agent appeler : "vols", "stock", ou "rappels"
2. Extraire les paramètres nécessaires pour cet agent sous forme de JSON valide
3. Si rien ne correspond, réponds {"agent": "none", "params": {}}

Exemples:
- "Quels vols pour Paris demain ?" => {"agent": "vols", "params": {"destination": "Paris", "date": "demain"}}
- "Stock de produit XYZ" => {"agent": "stock", "params": {"produit": "XYZ"}}
"""

    try:
        # Préparation des messages pour Groq
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]

        # Appel au LLM via langchain_groq
        response = groq_client.predict_messages(messages)
        response_text = response.content.strip()
        logger.info(f"Réponse LLM: {response_text}")

        # Parse la réponse JSON
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error("Réponse LLM non valide JSON")
            raise ValueError("Format de réponse invalide JSON")

        agent = parsed.get("agent")
        params = parsed.get("params", {})

        if agent not in AGENT_URLS:
            logger.info("Aucun agent approprié détecté")
            return {"status": "unknown", "message": "Aucun agent approprié détecté."}

        # Appel à l'agent approprié
        async with httpx.AsyncClient(timeout=TIMEOUT) as http_client:
            try:
                if agent == "stock":
                    payload = {"input": message}  # on envoie tout le message utilisateur tel quel
                else:
                    payload = params

                res = await http_client.post(
                    AGENT_URLS[agent],
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                res.raise_for_status()
                return {
                    "status": "success",
                    "called_agent": agent,
                    "response": res.json()
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"Erreur HTTP: {e}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Erreur de communication avec l'agent {agent}"
                )
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Erreur interne du serveur"
                )

    except Exception as e:
        logger.error(f"Erreur globale: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    uvicorn.run("master_agent:app", host="0.0.0.0", port=8000)
