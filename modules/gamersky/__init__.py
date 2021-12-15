import re

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.pattern import FullMatch, WildcardMatch, ArgumentMatch, RegexMatch
from graia.ariadne.message.parser.twilight import Twilight, Sparkle
from graia.ariadne.model import Friend, Group
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.event import SayaModuleInstalled

from common.schedule_job_helper import ScheduleJobHelper
from common.utils import load_config, save_config
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

config_path = 'modules/gamersky/config.json'
config = load_config(config_path)
schedule_helper = ScheduleJobHelper(channel)


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                Sparkle(
                    matches={
                        "header": FullMatch("gs-admin"),
                        "fetch_arg": ArgumentMatch("--fetch", "-f", optional=True),
                        "schedule_arg": ArgumentMatch("--schedule", "-s", optional=True),
                        "schedule_enable_arg": ArgumentMatch("--enable-schedule", "-e", optional=True),
                        # "param": WildcardMatch(optional=True),
                    },
                )
            )
        ],
    )
)
async def friend_message_listener(app: Ariadne, friend: Friend,
                                  fetch_arg: ArgumentMatch,
                                  schedule_arg: ArgumentMatch,
                                  schedule_enable_arg: ArgumentMatch
                                  # param: WildcardMatch
                                  ):
    try:
        if fetch_arg.matched:
            index = fetch_arg.result.asDisplay()
            count = fetchPage(index)
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f'fetch article count:{count}')]))
        elif schedule_enable_arg.matched:
            p = schedule_enable_arg.result.asDisplay()
            print(f"receive param:{p}")
            config['schedule'] = int(p)
            save_config(config_path, config)
            if not int(p):
                schedule_helper.removeAllJob()
        elif schedule_arg.matched:
            scheduleRules = schedule_arg.result.asDisplay()
            scheduleRules = re.sub(r":", " ", scheduleRules)
            schedule_helper.addScheduleJob("schedule_send_pic", schedule_send_pic, scheduleRules)
    except ValueError:
        await app.sendFriendMessage(friend, MessageChain.create([Plain(__usage__)]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                Sparkle(
                    matches={
                        "header": FullMatch("gs-admin"),
                        "fetch_arg": ArgumentMatch("--fetch", "-f", optional=True),
                        "schedule_arg": ArgumentMatch("--schedule", "-s", optional=True),
                        "schedule_enable_arg": ArgumentMatch("--enable-schedule", "-e", optional=True),
                        "subscribe_arg": ArgumentMatch("--subscribe", "-sub", "-S", optional=True),
                        # "param": WildcardMatch(optional=True),
                    },
                )
            )
        ],
    )
)
async def group_admin_manage_handle(app: Ariadne, group: Group,
                                    fetch_arg: ArgumentMatch,
                                    schedule_arg: ArgumentMatch,
                                    schedule_enable_arg: ArgumentMatch,
                                    subscribe_arg: ArgumentMatch
                                    ):
    try:
        if fetch_arg.matched:
            index = fetch_arg.result.asDisplay()
            count = fetchPage(index)
            await app.sendGroupMessage(group, MessageChain.create([Plain(f'fetch article count:{count}')]))
        elif schedule_enable_arg.matched:
            p = schedule_enable_arg.result.asDisplay()
            print(f"receive param:{p}")
            config['schedule'] = int(p)
            save_config(config_path, config)
            if not int(p):
                schedule_helper.removeAllJob()
            # updateSchedule()
        elif schedule_arg.matched:
            scheduleRules = schedule_arg.result.asDisplay()
            scheduleRules = re.sub(r":", " ", scheduleRules)
            schedule_helper.addScheduleJob("schedule_send_pic", schedule_send_pic, scheduleRules)
        elif subscribe_arg.matched:
            sub = subscribe_arg.result.asDisplay()
            if sub in ['1', 'true', 'True'] and group not in config['sub_list']:
                config['sub_list'].append(group.id)
                msg = '订阅成功'
            else:
                config['sub_list'].remove(group.id)
                msg = '取消订阅成功'
            save_config(config_path, config)
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
    except ValueError:
        await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))


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


async def schedule_send_pic(app: Ariadne):
    for group_id in config['sub_list']:
        picPath = getPicByType(int(TYPE_RANDOM))
        print(f"send pic path:{picPath}")
        await app.sendGroupMessage(group_id,
                                   MessageChain.create(
                                       [Image(path=picPath), Plain(picPath[picPath.rindex("/") + 2:-4])]))
