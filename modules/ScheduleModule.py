from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Member, Group, Friend, MemberPerm
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.event import SayaModuleInstalled

from config import ScheduleTask
from config.config import global_config_manager
from schedule.ScheduleMessageEvent import ScheduleMessageEvent
from schedule.schedule_job_helper import ScheduleJobHelper

channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[SayaModuleInstalled]
))
async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功！！")


schedule_helper = ScheduleJobHelper(channel)
schedule_tasks = global_config_manager.getAllScheduleTasks()


async def dispatch_schedule_job(app: Ariadne, schedule_task: ScheduleTask):
    print(f"dispatch_schedule_job:{schedule_task}")
    message_chain = MessageChain.create([Plain(schedule_task.command)])
    for g in schedule_task.subscribe_group:
        group = Group(
            id=g,
            name="",
            permission=MemberPerm.Member
        )
        member = Member(
            memberName="",
            group=group,
            id=g,
            permission=MemberPerm.Member
        )
        event = GroupMessage(
            messageChain=message_chain,
            sender=member
        )
        app.broadcast.postEvent(event)

    for u in schedule_task.subscribe_user:
        friend = Friend(
            id=u,
            nickname='',
            remark=''
        )
        event = FriendMessage(
            sender=friend,
            messageChain=message_chain
        )
        app.broadcast.postEvent(event)


if schedule_tasks:
    for task in list(filter(lambda x: x.enable, schedule_tasks)):
        schedule_helper.addScheduleJob(task, dispatch_schedule_job)


@channel.use(
    ListenerSchema(
        listening_events=[ScheduleMessageEvent]
    )
)
async def handle_schedule_event(schedule_task: ScheduleTask):
    print(f"handle_schedule_event:{schedule_task}")
    global_config_manager.addOrUpdateScheduleTask(schedule_task)
    schedule_helper.addScheduleJob(schedule_task, dispatch_schedule_job)
