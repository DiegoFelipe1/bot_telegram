import requests
import base64

credentials = {
  "client_id": "Client_Id_778e9124b5b447eb9bbe6209ab0e70b85a14d9b9",
  "client_secret": "Client_Secret_5a02f8e3a5a3f86e84db5665a06c45f640042817",
}

certificado = r"C:\Users\fdieg\Desktop\BOT PARA VENDAs\certificadoHOM.pem"  # A variável certificado é o diretório em que seu certificado em formato .pem deve ser inserido

auth = base64.b64encode(
  (f"{credentials['client_id']}:{credentials['client_secret']}"
   ).encode()).decode()

url = "https://pix-h.api.efipay.com.br/oauth/token" #Para ambiente de Desenvolvimento

payload="{\r\n    \"grant_type\": \"client_credentials\"\r\n}"
headers = {
  'Authorization': f"Basic {auth}",
  'Content-Type': 'application/json'
}

response = requests.request("POST",
                          url,
                          headers=headers,
                          data=payload,
                          cert=certificado)
def token_access():
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Erro ao gerar token", response.status_code, response.text)
    return None

