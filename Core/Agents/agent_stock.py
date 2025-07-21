from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
from typing import TypedDict

class StockAgentState(TypedDict):
    input: str
    output: str

# Charge la clé GROQ_API_KEY
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

os.environ["GROQ_API_KEY"] = groq_api_key

# Import des outils améliorés
try:
    from Core.tools.tools_stock import (
        get_low_stock_products,
        get_out_of_stock_products,
        get_category_statistics,
        get_product_restock_date,
        get_stock_overview,
        get_product_category,
        get_product_stock_quantity
    )
    print("✅ Outils importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import des outils : {e}")
    exit(1)

# Liste des outils
tools = [
    get_low_stock_products,
    get_out_of_stock_products,
    get_category_statistics,
    get_product_restock_date,
    get_stock_overview,
    get_product_category,
    get_product_stock_quantity
]

# Test d'un outil
print("\n=== Test d'un outil ===")
test_result = get_low_stock_products.invoke({"input_text": ""})
print(test_result[:200] + "..." if len(test_result) > 200 else test_result)

# Initialise le modèle Groq
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192"
)

# Initialise l'agent avec le type ZERO_SHOT_REACT_DESCRIPTION
agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Changé ici !
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3
)
# Après avoir créé agent_executor, ajoutez :
agent_executor.agent.llm_chain.prompt.template = """Tu es un assistant de gestion de stock qui répond en français.

RÈGLES IMPORTANTES:
- Utilise EXACTEMENT les noms de produits donnés par l'utilisateur
- Ne traduis JAMAIS les noms de produits (garde "Produit_1" comme "Produit_1")

""" + agent_executor.agent.llm_chain.prompt.template


# Fonction principale du graphe
def stock_agent_step(state):
    user_input = state["input"]
    print(f"📥 Input reçu: {user_input}")
    
    try:
        result = agent_executor.invoke({"input": user_input})
        print(f"📤 Résultat de l'agent: {result}")
        
        # Extraire la réponse
        if isinstance(result, dict):
            output = result.get("output", "Aucune réponse générée")
        else:
            output = str(result)
            
        # Vérifier si l'output est vide
        if not output or output.strip() == "":
            output = "❌ L'agent n'a pas pu générer de réponse. Veuillez reformuler votre question."
            
        return {"input": user_input, "output": output}
    
    except Exception as e:
        error_msg = f"❌ Erreur lors de l'exécution de l'agent: {str(e)}"
        print(error_msg)
        return {"input": user_input, "output": error_msg}

# Construction du graphe LangGraph
graph = StateGraph(StockAgentState)
graph.add_node("gestion_stock", stock_agent_step)
graph.set_entry_point("gestion_stock")
graph.add_edge("gestion_stock", END)

workflow = graph.compile()

# Test du graphe
if __name__ == "__main__":
    questions = [
       # "Montre-moi les produits avec les stocks les plus bas",
        #"Quels sont les produits en rupture de stock ?",
        #"Donne-moi les statistiques par catégorie",
        #"Donne-moi un aperçu général du stock" ,
        # "Produit_1 de quoi s'agit t-il ?" , 
        #"Catigorie des Produit_1 ?",
        #"Quantité en stock Produit_1 ?",
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print(f"{'='*60}")
        
        try:
            result = workflow.invoke({"input": question})
            print(f"✅ Réponse:\n{result['output']}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "-"*60)