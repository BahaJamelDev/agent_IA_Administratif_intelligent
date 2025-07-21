import pandas as pd
from langchain.tools import tool
import os

# === Chargement des données ===
file_path = "data/Agent_Administratif_SFM_Dataset.xlsx"

try:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

    df_stock = pd.read_excel(file_path, sheet_name="Gestion_Stock")
    print(f"✅ Données chargées avec succès : {len(df_stock)} lignes")
    print("Colonnes disponibles :", list(df_stock.columns))

except Exception as e:
    print(f"❌ Erreur lors du chargement des données : {e}")
    df_stock = pd.DataFrame()

# === Fonctions utilitaires ===
def check_data(columns_required: list = None) -> str | None:
    if df_stock.empty:
        return "❌ Erreur : Données non disponibles"
    if columns_required:
        for col in columns_required:
            if col not in df_stock.columns:
                return f"❌ Erreur : Colonne requise '{col}' manquante"
    return None

# === OUTILS ===

@tool
def get_low_stock_products(input_text: str = "") -> str:
    """Liste les 10 produits avec les niveaux de stock les plus faibles."""
    if (err := check_data(['Quantité_En_Stock'])):
        return err

    low_stock = df_stock.nsmallest(10, 'Quantité_En_Stock')
    result = "📊 PRODUITS AVEC LES STOCKS LES PLUS BAS :\n" + "=" * 50 + "\n"
    for _, row in low_stock.iterrows():
        seuil = f" (Seuil: {row['Seuil_Alert']})" if 'Seuil_Alert' in row else ""
        result += f"• {row['Produit']}: {row['Quantité_En_Stock']} unités{seuil}\n"
    return result

@tool
def get_out_of_stock_products(input_text: str = "") -> str:
    """Liste les produits en rupture de stock."""
    if (err := check_data(['Quantité_En_Stock', 'Seuil_Alert'])):
        return err

    ruptures = df_stock[df_stock["Quantité_En_Stock"] <= df_stock["Seuil_Alert"]]
    if ruptures.empty:
        return "✅ Aucun produit en rupture de stock actuellement."

    result = "🚨 PRODUITS EN RUPTURE DE STOCK :\n" + "=" * 50 + "\n"
    for _, row in ruptures.iterrows():
        result += f"• {row['Produit']}: {row['Quantité_En_Stock']} unités (Seuil: {row['Seuil_Alert']})\n"
    return result

@tool
def get_category_statistics(input_text: str = "") -> str:
    """Statistiques de stock par catégorie."""
    if (err := check_data(['Catégorie', 'Produit', 'Quantité_En_Stock'])):
        return err

    stats = df_stock.groupby("Catégorie").agg({
        "Produit": "count",
        "Quantité_En_Stock": ["sum", "mean"]
    }).round(2)

    stats.columns = ['Nombre_Produits', 'Stock_Total', 'Stock_Moyen']
    result = "📈 STATISTIQUES PAR CATÉGORIE :\n" + "=" * 50 + "\n"
    for categorie, row in stats.iterrows():
        result += (f"🏷️  {categorie}:\n"
                   f"   • Nombre de produits: {row['Nombre_Produits']}\n"
                   f"   • Stock total: {row['Stock_Total']}\n"
                   f"   • Stock moyen: {row['Stock_Moyen']}\n\n")
    return result

@tool
def get_product_restock_date(product_name: str) -> str:
    """Donne la date de dernier réapprovisionnement d’un produit donné."""
    if (err := check_data(['Produit', 'Quantité_En_Stock'])):
        return err

    produit = df_stock[df_stock["Produit"].str.contains(product_name, case=False, na=False)]
    if produit.empty:
        suggestions = df_stock[df_stock["Produit"].str.contains(product_name[:3], case=False, na=False)]
        msg = f"❌ Produit '{product_name}' non trouvé."
        if not suggestions.empty:
            msg += f"\nProduits similaires : {', '.join(suggestions['Produit'].head(3))}"
        return msg

    row = produit.iloc[0]
    result = ("📅 INFORMATIONS SUR LE PRODUIT :\n" + "=" * 50 + "\n"
              f"🏷️  Produit: {row['Produit']}\n"
              f"📦 Stock actuel: {row['Quantité_En_Stock']} unités\n")
    if 'Dernier_Réappro' in row:
        result += f"📅 Dernier réapprovisionnement: {row['Dernier_Réappro']}\n"
    if 'Seuil_Alert' in row:
        result += f"⚠️  Seuil d'alerte: {row['Seuil_Alert']}\n"
    return result

@tool
def get_stock_overview(input_text: str = "") -> str:
    """Résumé global du stock."""
    if (err := check_data(['Quantité_En_Stock'])):
        return err

    total_products = len(df_stock)
    total_stock = df_stock['Quantité_En_Stock'].sum()
    avg_stock = df_stock['Quantité_En_Stock'].mean()
    ruptures = len(df_stock[df_stock["Quantité_En_Stock"] <= df_stock["Seuil_Alert"]]) if 'Seuil_Alert' in df_stock.columns else "N/A"
    categories = df_stock['Catégorie'].nunique() if 'Catégorie' in df_stock.columns else "N/A"

    return (
        "📊 APERÇU GÉNÉRAL DU STOCK :\n" + "=" * 50 + "\n"
        f"📦 Total produits: {total_products}\n"
        f"📈 Stock total: {total_stock:,.0f} unités\n"
        f"📊 Stock moyen: {avg_stock:.1f} unités\n"
        f"🚨 Produits en rupture: {ruptures}\n"
        f"🏷️  Nombre de catégories: {categories}\n"
    )

@tool
def get_product_category(product_name: str) -> str:
    """Renvoie la catégorie d’un produit donné."""
    if (err := check_data(['Produit', 'Catégorie'])):
        return err

    produit = df_stock[df_stock["Produit"].str.contains(product_name, case=False, na=False)]
    if produit.empty:
        suggestions = df_stock[df_stock["Produit"].str.contains(product_name[:3], case=False, na=False)]
        msg = f"❌ Produit '{product_name}' non trouvé."
        if not suggestions.empty:
            msg += "\n\n🔍 Produits similaires trouvés :\n"
            for i, suggestion in enumerate(suggestions.head(5)["Produit"], 1):
                cat = df_stock[df_stock["Produit"] == suggestion]["Catégorie"].iloc[0]
                msg += f"   {i}. {suggestion} → {cat}\n"
        return msg

    row = produit.iloc[0]
    return (
        "🏷️  CATÉGORIE DU PRODUIT :\n" + "=" * 50 + "\n"
        f"📦 Produit: {row['Produit']}\n"
        f"🏷️  Catégorie: {row['Catégorie']}\n"
    )

@tool
def get_product_stock_quantity(product_name: str) -> str:
    """
    Renvoie la quantité en stock pour un produit donné.
    Utilisez cet outil lorsque l'utilisateur demande combien d'unités il reste pour un produit spécifique.
    """
    if (err := check_data(['Produit', 'Quantité_En_Stock'])):
        return err

    produit = df_stock[df_stock["Produit"].str.contains(product_name, case=False, na=False)]
    
    if produit.empty:
        suggestions = df_stock[df_stock["Produit"].str.contains(product_name[:3], case=False, na=False)]
        msg = f"❌ Produit '{product_name}' non trouvé."
        if not suggestions.empty:
            msg += "\n\n🔍 Produits similaires trouvés :\n"
            for i, suggestion in enumerate(suggestions.head(5)["Produit"], 1):
                msg += f"   {i}. {suggestion}\n"
        return msg

    row = produit.iloc[0]
    return (
        "📦 QUANTITÉ EN STOCK :\n" + "=" * 50 + "\n"
        f"🏷️  Produit: {row['Produit']}\n"
        f"📦 Quantité en stock: {row['Quantité_En_Stock']} unités\n"
    )


# === Tests rapides ===
#if __name__ == "__main__":
    print("=== Test des outils optimisés ===")
    tools = [
        get_low_stock_products,
        get_out_of_stock_products,
        get_category_statistics,
        get_product_restock_date,
        get_stock_overview,
        get_product_category
    ]

    for tool in tools:
        print(f"\n--- Test {tool.name} ---")
        try:
            args = {"product_name": "Produit_49"} if tool.name == "get_product_restock_date" or tool.name == "get_product_category" else {"input_text": ""}
            print(tool.invoke(args))
        except Exception as e:
            print(f"Erreur: {e}")
