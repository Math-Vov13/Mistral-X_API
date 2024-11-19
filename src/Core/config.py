from dataclasses import dataclass

@dataclass
class Config:
    NAME= "Mistral-X API"
    VERSION= "1.0.0"
    DESCRIPTION= """This API was developped using <u>FastAPI</u>!
    """

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

CONFIG = Config()