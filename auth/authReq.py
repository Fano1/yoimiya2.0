import websocket
import json
import os
from api import key
VTS_WEBSOCKET_URL = "ws://127.0.0.1:8001"
TOKEN_FILE = "token.json"

PLUGIN_NAME = "FanoPlugin"
PLUGIN_DEV = "Fano"


def check_auth():

    try:
        ws = websocket.create_connection(VTS_WEBSOCKET_URL)
        print("[WS] Connected to VTS.")

        auth_msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "check-auth-1",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEV,
                "authenticationToken": token
            }
        }

        ws.send(json.dumps(auth_msg))
        response = json.loads(ws.recv())

        chekc = {
	        "apiName": "VTubeStudioPublicAPI",
	        "apiVersion": "1.0",
	        "requestID": "SomeID",
	        "messageType": "HotkeysInCurrentModelRequest"}


        ws.send(json.dumps(chekc))
        res = json.loads(ws.recv())

        print(res)

        if response.get("data", {}).get("authenticated"):
            print("[AUTH] Successfully authenticated with VTS.")
        else:
            print("[AUTH] Authentication failed.")
            print(response)
        ws.close()
    except Exception as e:
        print(f"[ERROR] {e}")


#  Run this
if __name__ == "__main__":
    check_auth()
    
