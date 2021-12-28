from graia.broadcast import DispatcherInterface
from graia.broadcast.entities.dispatcher import BaseDispatcher

from config import ScheduleTask


class JobNameDispatcher(BaseDispatcher):

    def __init__(self, schedule_task: ScheduleTask):
        self.schedule_task = schedule_task

    async def catch(self, interface: DispatcherInterface):
        if interface.annotation is ScheduleTask:
            return self.schedule_task
        return None
