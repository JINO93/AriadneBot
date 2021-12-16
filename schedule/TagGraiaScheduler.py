import string
from typing import List, Optional

from graia.broadcast import Decorator
from graia.scheduler import GraiaScheduler, Timer, SchedulerTask
from graia.broadcast.typing import T_Dispatcher


class TagGraiaScheduler(GraiaScheduler):

    def scheduleWithTag(
            self,
            tag: string,
            timer: Timer,
            cancelable: bool = False,
            dispatchers: List[T_Dispatcher] = None,
            decorators: Optional[List[Decorator]] = None,
    ):
        """计划一个新任务.

        Args:
            tag (string): 定时任务的名字
            timer (Timer): 该定时任务的计时器.
            cancelable (bool, optional): 能否取消该任务. 默认为 False.
            dispatchers (List[T_Dispatcher], optional): 该任务要使用的 Dispatchers. 默认为空列表.
            decorators (Optional[List[Decorator]], optional): 该任务要使用的 Decorators. 默认为空列表.

        Returns:
            Callable[T_Callable, T_Callable]: 任务 函数/方法 包装器.
        """

        def wrapper(func):
            task = SchedulerTask(
                func,
                timer,
                self.broadcast,
                self.loop,
                cancelable,
                dispatchers,
                decorators,
            )
            task.tag = tag
            self.schedule_tasks.append(task)
            task.setup_task()
            return func

        return wrapper
