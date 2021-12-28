from graia.ariadne.event import MiraiEvent
from graia.broadcast import DispatcherInterface
from graia.broadcast.entities.dispatcher import BaseDispatcher

from config import ScheduleTask


class ScheduleMessageEvent(MiraiEvent):
    type: str = "ScheduleMessageEvent"
    task: ScheduleTask

    class Dispatcher(BaseDispatcher):
        # mixin = [MessageChainDispatcher, ApplicationDispatcher, SourceDispatcher]

        @staticmethod
        async def catch(interface: DispatcherInterface["ScheduleMessageEvent"], **kwargs):
            if interface.annotation is ScheduleTask:
                return interface.event.task
