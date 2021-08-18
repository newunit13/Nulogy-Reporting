import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

_credential = DefaultAzureCredential()

keyVaultName = os.environ["AZURE_VAULT_NAME"]
KVUri = f"https://{keyVaultName}.vault.azure.net"

client = SecretClient(vault_url=KVUri, credential=_credential)

print(client.get_secret("NulogyUsername").value)