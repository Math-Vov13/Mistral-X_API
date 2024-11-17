import httpx
from time import sleep as wait

max_requests = 10
payload = {
  "model": "mixtralai",
  "messages": [
    {
      "content": "Bonjour!",
      "role": "user"
    }
  ]
}

def main():
    base_url = "http://127.0.0.1:8000/api/v1"
    EndPoints = [
        {"endpoint": "/", "method": "GET"},
        {"endpoint": "/sessions/", "method": "GET"},
        {"endpoint": "/models/", "method": "GET"},

        {"endpoint": "/sessions/", "method": "POST"},
        {"endpoint": "/sessions/1234/models/completions", "method": "POST", "payload": True},
        {"endpoint": "/models/completions", "method": "POST", "payload": True},

        {"endpoint": "/sessions/1234", "method": "DELETE"},
        {"endpoint": "/models/test", "method": "DELETE"}
    ]
    
    for endpoint_dict in EndPoints:
        print(endpoint_dict)
        try:
            client = httpx.Client() # Create Client each loop

            # Create request
            req = client.build_request(
                    method= endpoint_dict.get("method"),
                    url= base_url + endpoint_dict.get("endpoint"),

                    json= payload if endpoint_dict.get("payload") else None
                )
            
            too_many_req = 0

            # Send Requests
            for _ in range(max_requests):
                response = client.send(request= req) # Send Request
                print(response, response.content.decode("utf-8")[:100])

                if response.status_code == 429:
                    too_many_req += 1 # requête bloquée par le rate limit
                wait(.3)

        except:
            pass
        else:
            print(f">> Un total de {too_many_req}/{max_requests} paquets ont été bloqués par l'API !", end="\n\n")

if __name__ == "__main__":
    main()