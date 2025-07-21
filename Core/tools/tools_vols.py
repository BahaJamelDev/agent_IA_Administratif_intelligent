import pandas as pd
from datetime import datetime
from typing import Optional

# Chargement des données (cache simple)
_flight_data_cache = None

def load_flight_data(path="data/Agent_Administratif_SFM_Dataset.xlsx", sheet="Billets_Avion") -> pd.DataFrame:
    global _flight_data_cache
    if _flight_data_cache is not None:
        return _flight_data_cache

    df = pd.read_excel(path, sheet_name=sheet)
    df["Date_Départ"] = pd.to_datetime(df["Date_Départ"])
    df["Prix (€)"] = pd.to_numeric(df["Prix (€)"], errors="coerce")
    _flight_data_cache = df
    return df

def filter_flights(destination: Optional[str], max_price: Optional[float], date_str: Optional[str]) -> str:
    df = load_flight_data()
    filtered = df.copy()

    if destination:
        filtered = filtered[filtered["Destination"].str.lower().str.contains(destination.lower())]

    if max_price is not None:
        filtered = filtered[filtered["Prix (€)"] <= max_price]

    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
            filtered = filtered[filtered["Date_Départ"].dt.date == date_obj]
        except:
            return "❌ Format de date invalide (utilisez jj/mm/aaaa)."

    if filtered.empty:
        return "❌ Aucun billet trouvé avec les critères donnés."

    lignes = []
    for _, row in filtered.iterrows():
        lignes.append(
            f"{row['Date_Départ'].strftime('%d/%m/%Y')} | {row['Destination']} | {row['Prix (€)']}€ | "
            f"{row.get('Compagnie', 'N/A')} | {row.get('Classe', 'Économique')}"
        )

    return "✈️ Billets trouvés :\n" + "\n".join(lignes)
