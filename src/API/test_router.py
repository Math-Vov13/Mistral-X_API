from fastapi import FastAPI, HTTPException, Query
from typing import Optional

app = FastAPI()

@app.post("/api/v1/models/{model_id}")
async def send_prompt_to_model(
    model_id: str,
    prompt: str,
    session_id: Optional[str] = Query(None)  # session_id est optionnel
):
    if session_id:
        # Appel avec session_id
        return await send_prompt_with_session(session_id, model_id, prompt)
    else:
        # Appel sans session_id
        return await send_prompt_without_session(model_id, prompt)

# Fonction qui gère l'envoi de prompt sans session
async def send_prompt_without_session(model_id: str, prompt: str):
    # Logique de traitement pour envoyer une requête au modèle sans session
    # Exemple fictif de retour
    return {
        "status": "success",
        "message": f"Prompt '{prompt}' envoyé au modèle '{model_id}' sans session"
    }

# Fonction qui gère l'envoi de prompt avec session
async def send_prompt_with_session(session_id: str, model_id: str, prompt: str):
    # Logique de traitement pour envoyer une requête au modèle avec une session
    # Exemple fictif de retour
    return {
        "status": "success",
        "message": f"Prompt '{prompt}' envoyé au modèle '{model_id}' avec la session '{session_id}'"
    }
