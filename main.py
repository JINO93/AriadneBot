import asyncio
import os

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.friend import Friend

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))

#app = GraiaMiraiApplication(
#    broadcast=bcc,
 #   connect_info=Session(
  #      host='http://localhost:8080',
   #     authKey='jino_ser',
    #    account='1834240938',
     #   websocket=True
#    )
#)

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
    for module in os.listdir("modules"):
        if module in ignore:
            continue
        try:
            if os.path.isdir(module):
                saya.require(f"modules.{module}")
            else:
                saya.require(f"modules.{module.split('.')[0]}")
        except ModuleNotFoundError:
            pass

@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    await app.sendFriendMessage(friend, MessageChain.create([
        Plain("Hello, World!")
    ]))

#app.launch_blocking()

try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()
