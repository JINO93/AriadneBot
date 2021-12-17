import re
import string

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
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler.timers import crontabify

from common.utils import load_config, save_config
from modules.gamersky.gamersky_sub import getPicByType, fetchPage, TYPE_DEFAULT, TYPE_GIF, TYPE_RANDOM
from schedule.schedule_job_helper import ScheduleJobHelper

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


group_admin_twilight = Twilight(
    Sparkle(
        [RegexMatch("gs-admin")],
        matches={
            "fetch_arg": ArgumentMatch("--fetch", "-f", optional=True),
            "schedule_arg": ArgumentMatch("--schedule", "-s", optional=True),
            "schedule_enable_arg": ArgumentMatch("--enable-schedule", "-e", optional=True),
            "subscribe_arg": ArgumentMatch("--subscribe", "-sub", "-S", optional=True),
            "unsubscribe_arg": ArgumentMatch("--unsubscribe", "-unsub", "-U", optional=True),
            "schedule_list_arg": RegexMatch("list", optional=True),
            "schedule_cancel_arg": ArgumentMatch("--sucheduler-cancel", '-sc', optional=True)
        },
    )
)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            group_admin_twilight
        ],
    )
)
async def group_admin_manage_handle(app: Ariadne, group: Group,
                                    fetch_arg: ArgumentMatch,
                                    schedule_arg: ArgumentMatch,
                                    schedule_enable_arg: ArgumentMatch,
                                    subscribe_arg: ArgumentMatch,
                                    unsubscribe_arg: ArgumentMatch,
                                    schedule_list_arg: RegexMatch,
                                    schedule_cancel_arg: ArgumentMatch
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
            schedule_conmand = schedule_arg.result.asDisplay()
            schedule_conmand_split = schedule_conmand.split("@")
            rule = schedule_conmand_split[0]
            sche_name = ''
            if len(schedule_conmand_split) >= 2:
                sche_name = schedule_conmand_split[1]
            rule = re.sub(r":", " ", rule)
            if not sche_name in config['schedule_tasks']:
                config['schedule_tasks'][sche_name] = {}
            config['schedule_tasks'][sche_name]['rule'] = rule
            save_config(config_path, config)
            schedule_helper.addScheduleJob(sche_name, schedule_send_pic, rule)
            await app.sendGroupMessage(group, MessageChain.create([Plain(f'成功开启定时任务：{sche_name}')]))
        elif subscribe_arg.matched:
            sub = subscribe_arg.result.asDisplay()
            if sub in config['schedule_tasks']:
                if 'subscribe_list' in config['schedule_tasks'][sub] and \
                        group.id in config['schedule_tasks'][sub]['subscribe_list']:
                    msg = '已经订阅过了'
                else:
                    if 'subscribe_list' not in config['schedule_tasks'][sub]:
                        config['schedule_tasks'][sub]['subscribe_list'] = []
                    config['schedule_tasks'][sub]['subscribe_list'].append(group.id)
                    msg = '订阅成功'
                    save_config(config_path, config)
            else:
                msg = '频道不存在'
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif unsubscribe_arg.matched:
            sub = unsubscribe_arg.result.asDisplay()
            if sub in config['schedule_tasks']:
                if 'subscribe_list' in config['schedule_tasks'][sub] and \
                        group.id in config['schedule_tasks'][sub]['subscribe_list']:
                    msg = f'已经取消订阅{sub}'
                    config['schedule_tasks'][sub]['subscribe_list'].remove(group.id)
                    save_config(config_path, config)
                else:
                    msg = '没有订阅此频道'
            else:
                msg = '频道不存在'
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif schedule_list_arg.matched:
            job_name_list = config['schedule_tasks'].keys()
            msg = f"当前运行的频道总共({len(job_name_list)})：\r\n"
            for n in job_name_list:
                msg += f" {n} \r\n"
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif schedule_cancel_arg.matched:
            sub = schedule_cancel_arg.result.asDisplay()
            if sub in config['schedule_tasks']:
                config['schedule_tasks'].pop(sub)
                save_config(config_path, config)
                schedule_helper.removeJob(sub)
                msg = f'停止定时任务【{sub}】成功'
            else:
                msg = f'没有叫【{sub}】的定时任务'
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


async def schedule_send_pic(app: Ariadne, job_name: string):
    print(f"schedule_send_pic,name:{job_name}")
    subscribe_list_ = config['schedule_tasks'][job_name]['subscribe_list'] if 'subscribe_list' in \
                                                                              config['schedule_tasks'][job_name] else []
    for group_id in subscribe_list_:
        picPath = getPicByType(int(TYPE_RANDOM))
        print(f"send pic path:{picPath}")
        if picPath:
            await app.sendGroupMessage(group_id,
                                       MessageChain.create(
                                           [Image(path=picPath), Plain(picPath[picPath.rindex("/") + 2:-4])]))


@channel.use(
    SchedulerSchema(
        crontabify("45-55/1 12,18 * * 1-5 *")  # 分钟, 小时, 月, 日, 周, 秒
    )
)
async def schedule_fetch_data(app: Ariadne):
    fetchPage(1)
