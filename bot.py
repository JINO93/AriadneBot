import asyncio

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Friend, MiraiSession, Group

from modules.gamersky.gamersky_sub import fetchPage, getPicByType, TYPE_DEFAULT, TYPE_GIF, TYPE_RANDOM

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="jino_ser",  # 填入 verifyKey
        account=1834240938,  # 你的机器人的 qq 号
    )
)

__usage__ = "使用方法：lyf [type]"


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: Ariadne, friend: Friend, message: MessageChain):
    display = message.asDisplay()
    if not display.startswith("gs-fetch"):
        return
    try:
        display__split = display.split(" ")
        if len(display__split) > 3:
            await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))
            return
        comm1 = ''
        comm2 = '1'
        if len(display__split) == 2:
            comm1 = display__split[1]
        elif len(display__split) == 3:
            comm1 = display__split[1]
            comm2 = display__split[2]
        count = fetchPage(comm2)
        await app.sendFriendMessage(friend, MessageChain.create([Plain(f'fetch article count:{count}')]))
    except ValueError:
        await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))


@bcc.receiver("GroupMessage")
async def group_message_listener(app: Ariadne, group: Group, message: MessageChain):
    display = message.asDisplay()
    if not display.startswith("lyf"):
        return
    try:
        display__split = display.split(" ")
        if len(display__split) > 2:
            await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))
            return
        showType = TYPE_DEFAULT
        if len(display__split) == 2:
            picType = display__split[1]
            if picType in ['gif', 'Gif', "GIF", '0']:
                showType = TYPE_GIF
            elif picType in ['ran', 'random', '2']:
                showType = TYPE_RANDOM
            else:
                showType = TYPE_DEFAULT
        picPath = getPicByType(int(showType))
        print(f"send pic path:{picPath} showType:{showType}")
        await app.sendGroupMessage(group,
                                   MessageChain.create([Image(path=picPath), Plain(picPath[picPath.rindex("/") + 2:-4])]))
    except ValueError:
        await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))


loop.run_until_complete(app.lifecycle())
