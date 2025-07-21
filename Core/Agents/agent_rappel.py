from langgraph.graph import StateGraph, END
from typing import TypedDict
import pandas as pd

from Core.tools.mailer import send_email
from Core.tools.whatsapp import send_whatsapp_via_twilio
from Core.tools.tools_rappels import lire_donnees, generer_message

# Définir l'état partagé entre les noeuds
class RappelState(TypedDict, total=False):
    df: pd.DataFrame
    message: str

# Noeud 3 : envoyer email
def envoyer_email(state: RappelState) -> dict:
    send_email("Rappel des tâches", state["message"])
    return {}

# Noeud 4 : envoyer WhatsApp
def envoyer_whatsapp(state: RappelState) -> dict:
    send_whatsapp_via_twilio(state["message"], "+21696818563")
    return {}

# Créer le graphe avec le schéma
workflow = StateGraph(RappelState)

workflow.add_node("LireDonnées", lire_donnees)
workflow.add_node("GénérerMessage", generer_message)
workflow.add_node("EnvoyerEmail", envoyer_email)
workflow.add_node("EnvoyerWhatsApp", envoyer_whatsapp)

workflow.set_entry_point("LireDonnées")
workflow.add_edge("LireDonnées", "GénérerMessage")
workflow.add_edge("GénérerMessage", "EnvoyerEmail")
workflow.add_edge("EnvoyerEmail", "EnvoyerWhatsApp")
workflow.set_finish_point("EnvoyerWhatsApp")

# Compiler le graph
graph = workflow.compile()

# Lancer le graphe
if __name__ == "__main__":
    graph.invoke({})
    print("✅ Processus de rappel terminé.")
