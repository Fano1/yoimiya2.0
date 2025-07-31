import asyncio
import websockets
import json

VTS_WEBSOCKET_URL = "ws://127.0.0.1:8001"  # Change if needed

async def request_auth_token():
    async with websockets.connect(VTS_WEBSOCKET_URL) as ws:
        # Your auth token request message
        auth_token_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth-token-1",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "FanoPlugin",
                "pluginDeveloper": "Fano",
            }
        }

        # Send the request JSON
        await ws.send(json.dumps(auth_token_request))
        print("[WS] Sent AuthenticationTokenRequest!")

        # Wait for the response
        response = await ws.recv()
        print(f"[WS] Raw response: {response}")

        # Parse JSON response
        data = json.loads(response)
        token = data.get("data", {}).get("authenticationToken")
        if token:
            print(f"[Auth] Got token: {token}")
            return token
        else:
            print("[Auth] Failed to get token")
            print(data)
            return None

asyncio.run(request_auth_token())
