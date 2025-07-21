
from datetime import date
import pandas as pd

def lire_donnees(state):
    """Lit le fichier Excel et retourne le DataFrame."""
    df = pd.read_excel("data/Agent_Administratif_SFM_Dataset.xlsx", sheet_name="Rappels_Planning")
    df['Date_Echéance'] = pd.to_datetime(df['Date_Echéance']).dt.date
    return {"df": df}

def generer_message(state):
    """Génère le message à partir des tâches extraites."""
    df = state["df"]
    today = date.today()

    taches_du_jour = df[(df['Date_Echéance'] == today) & (df['Statut'] != 'Terminé')]
    taches_en_retard = df[(df['Date_Echéance'] < today) & (df['Statut'] != 'Terminé')]

    message = "📌 *Rappel des tâches*\n\n"
    if not taches_du_jour.empty:
        message += "✅ *Tâches du jour :*\n"
        for _, row in taches_du_jour.iterrows():
            message += f"- {row['Description']} (Priorité: {row['Priorité']})\n"
    if not taches_en_retard.empty:
        message += "\n⚠️ *Tâches en retard :*\n"
        for _, row in taches_en_retard.iterrows():
            message += f"- {row['Description']} (Échéance: {row['Date_Echéance']})\n"
    if message.strip() == "📌 *Rappel des tâches*":
        message += "🎉 Aucune tâche urgente aujourd'hui."

    return {"message": message}
