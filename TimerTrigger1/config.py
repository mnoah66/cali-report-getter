# config.py
from os import environ as env
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from dotenv import load_dotenv
load_dotenv() 

TENANT_ID = env.get("AZURE_TENANT_ID", "")
CLIENT_ID = env.get("AZURE_CLIENT_ID", "")
CLIENT_SECRET = env.get("AZURE_CLIENT_SECRET", "")
KEYVAULT_NAME = env.get("AZURE_KEYVAULT_NAME", "")

KEYVAULT_URI = f"https://{KEYVAULT_NAME}.vault.azure.net/"

_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

_sc = SecretClient(vault_url=KEYVAULT_URI, credential=_credential)

EMAIL_USERNAME = _sc.get_secret("DemoUserName").value
EMAIL_PASSWORD = _sc.get_secret("DemoUserNamePassword").value