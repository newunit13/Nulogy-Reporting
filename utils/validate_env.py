import os

print(f'Azure Tenant ID: {os.environ["AZURE_TENANT_ID"]}')
print(f'Azure Client ID: {os.environ["AZURE_CLIENT_ID"]}')
print(f'Azure Client Secret: {os.environ["AZURE_CLIENT_SECRET"]}')