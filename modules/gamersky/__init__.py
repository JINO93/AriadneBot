from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.pattern import FullMatch, WildcardMatch, ArgumentMatch
from graia.ariadne.message.parser.twilight import Twilight, Sparkle
from graia.ariadne.model import Friend, Group
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.event import SayaModuleInstalled

from modules.gamersky.gamersky_sub import getPicByType, fetchPage, TYPE_DEFAULT, TYPE_GIF, TYPE_RANDOM

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[SayaModuleInstalled]
))
async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功！！")


#
# 插件信息
__name__ = "Gamersky_information"
__description__ = "投喂Gamersky美图"
__author__ = "JINO"
__usage__ = "使用方法：lyf [type]"
#
saya = Saya.current()
channel = Channel.current()
#
channel.name(__name__)
channel.author(__author__)
channel.description(f"{__description__}\n{__usage__}")

__usage__ = "使用方法：lyf [type]"


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                Sparkle(
                    matches={
                        "header": FullMatch("gs-fetch"),
                        "arg": ArgumentMatch("page", optional=False),
                        "page_index": WildcardMatch(optional=True),
                    },
                )
            )
        ],
    )
)
async def friend_message_listener(app: Ariadne, friend: Friend, page_index: WildcardMatch):
    try:
        index = '1'
        if page_index.matched:
            index = page_index.result.asDisplay()
        count = fetchPage(index)
        await app.sendFriendMessage(friend, MessageChain.create([Plain(f'fetch article count:{count}')]))
    except ValueError:
        await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                Sparkle(
                    matches={
                        "header": FullMatch("lyf"),
                        "arg1": WildcardMatch(optional=True),
                    },
                )
            )
        ],
    )
)
async def group_message_listener(app: Ariadne, group: Group, arg1: WildcardMatch):
    try:
        showType = TYPE_DEFAULT
        if arg1.matched:
            picType = arg1.result.asDisplay()
            if picType in ['gif', 'Gif', "GIF", '0']:
                showType = TYPE_GIF
            elif picType in ['ran', 'random', '2']:
                showType = TYPE_RANDOM
            else:
                showType = TYPE_DEFAULT
        picPath = getPicByType(int(showType))
        print(f"send pic path:{picPath} showType:{showType}")
        await app.sendGroupMessage(group,
                                   MessageChain.create(
                                       [Image(path=picPath), Plain(picPath[picPath.rindex("/") + 2:-4])]))
    except ValueError:
        await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))
