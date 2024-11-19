from pydantic import BaseModel


### Sessions
Session_id_Schema = int

class newSession(BaseModel):
    __tablename__ = "Session"
    
    session_id: Session_id_Schema
    created: float
    history: dict | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 0,
                "created": 0.0,
                "history": {}
            }
        }


### Messages
Message_id_Schema = int