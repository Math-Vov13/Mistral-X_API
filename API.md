# API Project

- Gestion des ID Sessions
- Gestion des Clés API
- Gestion des limites de Tokens



- Creation de Session pour parler avec Mistral
- 


## Mots-clés
**API**: <u>Application Programming Interface</u>
- **Clé API**: C'est une clé sous la forme `API_1234_5678_90_ABCD`. Cette clé est nécessaire pour être authentifié dans l'API. La clé doit être comprise dans le Header de la requête, comme ceci : `{'Authorization': 'Bearer <api_key>'}`. Chaque utilisateur a un nombre limité de requêtes par jours.
- **Session**: Une Session correspond à un ensemble d'échanges entre un utilisateur et un modèle à travers l'API. Une session est unique et peut être retrouvée par son ID (session ID définie en-dessous). ***Une session peut être créée par un utilisateur, mais également supprimée***
- **Session ID**: Un '*ID de session*' ou '*identifiant de session*' est un token qui référence un historique de conversation.

**Modèles**: <u>Modèles d'intelligence artificielle</u>
- **IDK**: jsp

## Schema
DataBase:

## Fonctionalités
- Créer une clé API avec un compte dans la BDD
- Créer une Session -> ID Session

## Requêtes
-- Vous devez d'abord récupérer ou créer dans la Base de données une clé api --
</br>
Le Headers doit ressembler à ça:</br>
```json
{
    "Accept": "application/json",
    "Authorization": "Bearer <api_key>"
}
```
</br>

### Other
get
> - `Voir` la page Home
```js
GET /
```

> - `Voir` la page about
```js
GET /about
```

> - `Voir` la fausse page admin (redirection : Rickroll)
```js
GET /admin
```
</br>

### Documentation
get
> - `Voir` la doc
```js
GET /api/v1/docs
```

> - `Voir` la redoc
```js
GET /api/v1/redoc
```

> - `Voir` le fichier json openapi
```js
GET /api/v1/openapi.json
```
</br>

### Sessions
get
> - `Voir` toutes les sessions en cours
```js
GET /api/v1/sessions
```

> - `Voir` une session en cours avec son <u>'session_id'</u>
```js
GET /api/v1/sessions/{session_id}
```

> - `Voir` l'historique des conversations d'une session en cours avec son <u>'session_id'</u>
```js
GET /api/v1/sessions/{session_id}/history
```

post
> - `Créer` une session
```js
POST /api/v1/sessions
```

> - `Envoyer` un prompt à un modèle avec un <u>'session_id'</u>, <u>'model_id'</u> et <u>prompt</u>
```js
POST /api/v1/sessions/{session_id}/models/completions
{
    ...
}
```

delete
> - `Détruire` une session avec son <u>'session_id'</u>
```js
DELETE /api/v1/sessions/{session_id}
```

*NOTE*: créer un id pour chaque message. Pouvoir supprimer un message par son id ?

</br>

### Models
get
> - `Voir` tous les modèles disponibles
```js
GET /api/v1/models
```

> - `Voir` un modèle
```js
GET /api/v1/models/{model_id}
```

post
> - `Envoyer` une requête à l'agent avec son <u>'agent_id'</u> et <u>prompt</u> (sans sauvegarder l'historique dans une session)
```js
POST /api/v1/models/completions
{
    ...
}
```

delete
> - `Détruire` un prompt à un modèle avec un <u>'session_id'</u>, <u>'model_id'</u> et <u>prompt</u>
```js
DELETE /api/v1/models/{model_id}
{
    ...
}
```
</br>

### Agents
get
> - `Voir` les agents créés
```js
GET /api/v1/models/agents
```

> - `Voir` un agent et ses caractéristiques avec son <u>agent_id</u>
```js
GET /api/v1/models/agents/{agent_id}
```

post
> - `Créer` un agent avec son <u>name</u>
```js
POST /api/v1/models/agents?name={name}
```

> - `Envoyer` une requête à l'agent avec son <u>'agent_id'</u> et <u>prompt</u>
```js
POST /api/v1/models/agents/{agent_id}
{
    ...
}
```

> - `Envoyer` une requête à l'agent avec son <u>'agent_id'</u>, un <u>'session_id'</u> et <u>prompt</u>
```js
POST /api/v1/sessions/{session_id}/models/agents/{agent_id}
{
    ...
}
```

delete
> - `Détruire` un agent avec son <u>'agent_id'</u>
```js
DELETE /api/v1/models/agents/{agent_id}
```
</br>

### Fine-Tuning
Vide pour le moment...

API pour la création et la gestion d'agents de Mistral.