from typing import Callable, Any

from graia.broadcast import Broadcast
from graia.scheduler import SchedulerTask, Timer


class TagSchedulerTask(SchedulerTask):
    def __init__(self, tag, target: Callable[..., Any], timer: Timer, broadcast: Broadcast):
        super().__init__(target, timer, broadcast)
        self.tag = tag

