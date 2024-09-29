from fastapi.openapi.utils import get_openapi
from api_model.main import app
from api_model.predict import SinglePredictionInput, SinglePredictionOutput

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API OptimEAL",
        version="1.0.0",
        description="""
        API pour le modèle de prédiction OptimEAL.
        
        ## Architecture
        L'API est construite avec FastAPI et expose un modèle d'IA pour prédire la fréquentation de la cantine.
        Elle utilise une base de données SQL Server pour stocker les prédictions.
        
        ## Authentification
        L'API utilise une authentification par token JWT. Un token valide doit être inclus dans l'en-tête 
        'Authorization' de chaque requête, sous la forme 'Bearer <token>'.
        
        ## Accessibilité
        Cette documentation respecte les recommandations d'accessibilité de l'association Valentin Haüy, 
        notamment en utilisant une structure claire et des descriptions détaillées pour chaque endpoint.
        """,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Ajout des détails spécifiques pour l'endpoint /predict
    openapi_schema["paths"]["/predict"]["post"]["summary"] = "Effectue une prédiction"
    openapi_schema["paths"]["/predict"]["post"]["description"] = """
        Cet endpoint prend en entrée les données d'une journée et retourne une prédiction 
        de la fréquentation de la cantine pour cette journée.
    """
    openapi_schema["paths"]["/predict"]["post"]["responses"]["401"] = {
        "description": "Non authentifié"
    }
    openapi_schema["paths"]["/predict"]["post"]["responses"]["403"] = {
        "description": "Non autorisé"
    }
    openapi_schema["paths"]["/predict"]["post"]["responses"]["422"] = {
        "description": "Données d'entrée invalides"
    }
    
    # Ajout des schémas pour SinglePredictionInput et SinglePredictionOutput
    openapi_schema["components"]["schemas"]["SinglePredictionInput"] = {
        "type": "object",
        "properties": {
            "id_jour": {
                "type": "string",
                "format": "date",
                "description": "Date pour laquelle la prédiction est demandée"
            }
        },
        "required": ["id_jour"]
    }
    openapi_schema["components"]["schemas"]["SinglePredictionOutput"] = {
        "type": "object",
        "properties": {
            "prediction": {
                "type": "integer",
                "description": "Nombre prédit de repas pour la journée"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi