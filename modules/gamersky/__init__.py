import re
import string

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.pattern import FullMatch, WildcardMatch, ArgumentMatch, RegexMatch
from graia.ariadne.message.parser.twilight import Twilight, Sparkle
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler.timers import crontabify

from config.config import global_config_manager
from config.model import ScheduleTask
from modules.BaseModule import BaseModule
from modules.gamersky.gamersky_sub import getPicByType, fetchPage, TYPE_DEFAULT, TYPE_GIF, TYPE_RANDOM
from schedule.ScheduleMessageEvent import ScheduleMessageEvent

gamersky_module = BaseModule(Channel.current(), 'Gamersky_information', '投喂Gamersky美图', 'JINO')
__usage__ = "使用方法：lyf [type]"


@gamersky_module.use(
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
        #         gamersky_module.schedule_helper.removeAllJob()
        elif schedule_arg.matched:
            scheduleRules = schedule_arg.result.asDisplay()
            scheduleRules = re.sub(r":", " ", scheduleRules)
            gamersky_module.schedule_helper.addScheduleJob("schedule_send_pic", schedule_send_pic, scheduleRules)
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


@gamersky_module.use(
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
        #         gamersky_module.schedule_helper.removeAllJob()
        # updateSchedule()
        elif schedule_arg.matched:
            schedule_conmand = schedule_arg.result.asDisplay()
            try:
                rule, sche_name, command = schedule_conmand.split("@")
                rule = re.sub(r":", " ", rule)
                schedule_task = ScheduleTask(
                    name=sche_name,
                    rule=rule,
                    command=command
                )
                app.broadcast.postEvent(ScheduleMessageEvent(task=schedule_task))
                msg = f'成功开启定时任务：{sche_name}'
            except ValueError:
                msg = __usage__
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
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
            tasks = global_config_manager.getAllScheduleTasks()
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
                gamersky_module.schedule_helper.removeJob(sub)
                msg = f'停止定时任务【{sub}】成功'
            else:
                msg = f'没有叫【{sub}】的定时任务'
            await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))
    except ValueError:
        await app.sendGroupMessage(group, MessageChain.create([Plain(__usage__)]))


@gamersky_module.use(
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


@gamersky_module.use(
    SchedulerSchema(
        crontabify("45-55/1 12,18 * * 1-5 *")  # 分钟, 小时, 月, 日, 周, 秒
    )
)
async def schedule_fetch_data(app: Ariadne):
    fetchPage(1)

