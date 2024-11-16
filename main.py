from src.API.main import app

## Uncomment this line if 'uvicorn is not installed on your laptop'
import uvicorn
uvicorn.run(
    app= app
)