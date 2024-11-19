from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from copy import replace

from datetime import datetime
from src.Core.config import CONFIG
from src.API.endpoints.Sessions import router as rt_Sessions
from src.API.endpoints.Models import router as rt_Models
from src.API.endpoints.Auth import router as rt_Auth

# Examples:
# @router.options()
# @router.get()
# @router.head()
# @router.post()
# @router.put()
# @router.delete()
# @router.trace()


def create_app() -> FastAPI:
    # Client
    app = FastAPI(
        ## Informations
        title= CONFIG.NAME,
        description= CONFIG.DESCRIPTION,
        version= CONFIG.VERSION,
        contact= {
            "name": "...",
            # "url": "nothing here",
            # "email": "nothing here"
        },
        license_info= {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },

        ## UIs
        swagger_ui_parameters= {
            "syntaxHighlightTheme": "obsidian",  # Personnalise le thème de couleur
            "operationsSorter": "method"  # Trie les routes par méthode HTTP (GET en premier)
        },

        ## API metadata
        redirect_slashes= False,
        root_path= "/api/v1",
    )

    return app

app = create_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://127.0.0.1:8000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

templates = Jinja2Templates(directory="src/API/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")



## DOCS
# @app.get("/docs", tags=["API Documentation"],
#          summary="Accéder à Swagger UI")
# async def swagger_docs():
#     return RedirectResponse(url="/docs")

# # Route pour rediriger vers /redoc
# @app.get("/redoc", tags=["API Documentation"],
#          summary="Accéder à Redoc UI")
# async def redoc_docs():
#     return RedirectResponse(url="/redoc")

# # Route pour afficher le schéma OpenAPI en JSON
# @app.get("/openapi", tags=["API Documentation"],
#          summary="Voir le fichier OpenAPI en JSON")
# async def openapi_json():
#     return get_openapi(title=app.title, version=app.version, routes=app.routes)



## HOME
@app.get("/", response_class=HTMLResponse, tags= ["Home"],
         summary="Show Home Page",
         description="Home Page.")
async def home(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    print(token)
    return templates.TemplateResponse("index.html", {"request": request, "data": "Bienvenue!"})


@app.get("/about", response_class=HTMLResponse, tags= ["Home"],
         summary="Show About Page",
         description="About Page.")
async def about(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": "ABOUT !"})


@app.get("/admin", response_class=HTMLResponse, tags= ["Home"], include_in_schema= False,
         summary="Show Admin Page",
         description="Admin Page.")
async def admin(request: Request):
    access = False
    if not access:
        raise HTTPException(status_code = status.HTTP_418_IM_A_TEAPOT,
                            detail      = "Huh ho?! You're not supposed to be there...",
                            headers     = {"is_secret": "true", "code_error": "403", "method": "GET"})
    
    # Redirection vers une page web marrante :)
    return RedirectResponse(url= "https://rickrollwebsite.univer.se/secret")


@app.get("/debug", include_in_schema= False,
         summary= "",
         description= "[Hidden EndPoint] Show debug data")
async def debug(request: Request):
    return {
        "server": {
            "host": request.url.netloc,
            "date": datetime.now().timestamp(),
        },
        "url" : {
            "complete": "http" + ("s" if request.url.is_secure else "") + "://" + request.url.netloc + request.url.path,
            "uri": request.url.path,
            "method": request.method,
            "secured": request.url.is_secure,
        },

        "client": {
            "ip": request.client.host,
            "port": request.client.port,
        },

        "request": {
            "params": request.path_params.items(),
            "query": request.query_params.items(),
            "headers": request.headers.items(),
            "cookies": request.cookies.items(),
        }
    }



# ROUTERS
app.include_router(router= rt_Sessions)
app.include_router(router= rt_Models)
app.include_router(router= rt_Auth)


# @app.get("/index", response_class=HTMLResponse)
# async def serve_html(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request, "data": "Bienvenue!"})

# @app.get("/", response_class=HTMLResponse)
# def main():
#     html_content = """
#     <!DOCTYPE html>
#     <html lang="fr">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Document</title>
#     </head>
#     <body>
#         <h1>Bienvenue sur l'API !</h1>
#         <p>Pour accéder au schéma complet, rendez-vous à ces liens :</p>
#         <ol>
#             <ul><a href= "/docs">/docs</a></ul>
#             <ul><a href= "/redoc">/redoc</a></ul>
#         </ol>
#     </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)

# @app.get("/xml", response_class= HTMLResponse)
# def xml_attack(username: str):
#     from html import escape

#     #username = "Jean<script>alert('XSS')</script>"
#     escaped_username = escape(username)

#     html_content = f"""
#         <html>
#             <body>
#                 <h1>Bienvenue {username}!</h1>
#             </body>
#         </html>
#     """

#     return HTMLResponse(content=html_content)