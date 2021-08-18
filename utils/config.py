import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

_credential = DefaultAzureCredential()

_keyVaultName = os.environ["AZURE_VAULT_NAME"]
_KVUri = f"https://{_keyVaultName}.vault.azure.net"

_client = SecretClient(vault_url=_KVUri, credential=_credential)

NULOGY_SECRET_KEY   = _client.get_secret("NulogySecretKey").value
AZURE_DB_UN         = _client.get_secret("AzureDatabaseUsername").value
AZURE_DB_PW         = _client.get_secret("AzureDatabasePassword").value
