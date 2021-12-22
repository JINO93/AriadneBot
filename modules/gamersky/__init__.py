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
from graia.saya.event import SayaModuleInstalled, SayaModuleUninstall
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler.timers import crontabify

from config.config import global_config_manager
from config.model import ScheduleTask
from modules.gamersky.gamersky_sub import getPicByType, fetchPage, TYPE_DEFAULT, TYPE_GIF, TYPE_RANDOM
from schedule.schedule_job_helper import ScheduleJobHelper

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[SayaModuleInstalled]
))
async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功！！")


@channel.use(ListenerSchema(
    listening_events=[SayaModuleUninstall]
))
async def module_listener(event: SayaModuleUninstall):
    print(f"{event.module}::模块卸载ing！！")


#
# 插件信息
__name__ = "Gamersky_information"
__description__ = "投喂Gamersky美图"
__author__ = "JINO"
__usage__ = "使用方法：lyf [type]"
#
#
channel.name(__name__)
channel.author(__author__)
channel.description(f"{__description__}\n{__usage__}")

schedule_helper = ScheduleJobHelper(channel)
module_config = global_config_manager.getModuleConfig(channel.module)


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
            # todo 定时任务全局开关
        # elif schedule_enable_arg.matched:
        #     p = schedule_enable_arg.result.asDisplay()
        #     print(f"receive param:{p}")
        #     config['schedule'] = int(p)
        #     save_config(config_path, config)
        #     if not int(p):
        #         schedule_helper.removeAllJob()
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
        # elif schedule_enable_arg.matched:
        #     p = schedule_enable_arg.result.asDisplay()
        #     print(f"receive param:{p}")
        #     config['schedule'] = int(p)
        #     save_config(config_path, config)
        #     if not int(p):
        #         schedule_helper.removeAllJob()
        # updateSchedule()
        elif schedule_arg.matched:
            schedule_conmand = schedule_arg.result.asDisplay()
            schedule_conmand_split = schedule_conmand.split("@")
            rule = schedule_conmand_split[0]
            sche_name = ''
            if len(schedule_conmand_split) >= 2:
                sche_name = schedule_conmand_split[1]
            rule = re.sub(r":", " ", rule)
            schedule_task = ScheduleTask(
                module=channel.module,
                name=sche_name,
                rule=rule
            )
            global_config_manager.addOrUpdateScheduleTask(schedule_task)
            schedule_helper.addScheduleJob(sche_name, schedule_send_pic, rule)
            await app.sendGroupMessage(group, MessageChain.create([Plain(f'成功开启定时任务：{sche_name}')]))
        elif subscribe_arg.matched:
            sub = subscribe_arg.result.asDisplay()
            task = global_config_manager.getScheduleTask(sub)
            if task:
                if group.id in task.subscribe_group:
                    msg = '已经订阅过了'
                else:
                    msg = '订阅成功'
                    task.subscribe_group.append(group.id)
                    global_config_manager.addOrUpdateScheduleTask(task)
            else:
                msg = '频道不存在'
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif unsubscribe_arg.matched:
            sub = unsubscribe_arg.result.asDisplay()
            task = global_config_manager.getScheduleTask(sub)
            if task:
                if group.id in task.subscribe_group:
                    msg = f'已经取消订阅{sub}'
                    task.subscribe_group.remove(group.id)
                    global_config_manager.addOrUpdateScheduleTask(task)
                else:
                    msg = '没有订阅此频道'
            else:
                msg = '频道不存在'
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif schedule_list_arg.matched:
            tasks = global_config_manager.getScheduleTasksByModule(channel.module)
            count = len(tasks) if tasks else 0
            msg = f"当前运行的频道总共({count})：\r\n"
            if count:
                for n in tasks:
                    msg += f" {n.name} \r\n"
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
        elif schedule_cancel_arg.matched:
            sub = schedule_cancel_arg.result.asDisplay()
            task = global_config_manager.getScheduleTask(sub)
            if task:
                global_config_manager.deleteScheduleTask(task)
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
    task = global_config_manager.getScheduleTask(job_name)
    if task:
        for group_id in task.subscribe_group:
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


schedule_tasks = global_config_manager.getScheduleTasksByModule(channel.module)
if schedule_tasks:
    for task in schedule_tasks:
        print(f'开启定时任务【{task.name}】,规则为：{task.rule}')
        schedule_helper.addScheduleJob(task.name, schedule_send_pic, task.rule)
