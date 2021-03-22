import base64

username = ''
password = ''
secret_key = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')