from typing import ( Literal )

class History:
    def __init__(self, history: list[dict[str, str]] = []) -> None:
        self.__history = history
    
    def force_append(self, message):
        self.__history.append(message)
    
    def append(self, message: str, role: Literal["user", "assistant"] = "user"):
        if not message:
            message = "<ce champ est vide>"

        Response = {
            "role": role,
            "content": message
        }

        if self.lastResponse["role"] == role:
            pass
            #self.lastResponse = Response
        else:
            self.__history.append(Response)


    def __str__(self) -> str:
        return str(self.__history)

    @property
    def History(self) -> list:
        return self.__history
    
    @property
    def lastResponse(self) -> dict[str]:
        return self.__history[-1] if len(self.__history) > 0 else {"role": None, "content": None}