import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
import os
from dotenv import load_dotenv

load_dotenv()

character_id = os.getenv("CHARACTER_ID")
token = os.getenv("CHARACTER_TOKEN")
chat_id = os.getenv("CHAT_ID_NEW")

async def main():
    client = await get_client(token=token)

    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")

    # chat, greeting_message = await client.chat.create_chat(character_id)
    # print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

    try:
        while True:
            # NOTE: input() is blocking function!
            message = input(f"[{me.name}]: ")

            answer = await client.chat.send_message(character_id, chat_id, message)
            print(f"[{answer.author_name}]: {answer.get_primary_candidate().text}")
            # print(chat.chat_id)

    except SessionClosedError:
        print("session closed. Bye!")

    finally:
        # Don't forget to explicitly close the session
        await client.close_session()

asyncio.run(main())