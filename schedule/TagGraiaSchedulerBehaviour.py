from typing import Any

from graia.saya import Cube, Behaviour
from graia.scheduler.saya import SchedulerSchema

from schedule import TagGraiaScheduler


class TagGraiaSchedulerBehaviour(Behaviour):
    scheduler: TagGraiaScheduler

    def __init__(self, scheduler: TagGraiaScheduler) -> None:
        self.scheduler = scheduler

    def allocate(self, cube: Cube[SchedulerSchema]):
        if isinstance(cube.metaclass, SchedulerSchema):
            if hasattr(cube, 'tag'):
                self.scheduler.scheduleWithTag(
                    cube.tag,
                    cube.metaclass.timer,
                    cube.metaclass.cancelable,
                    cube.metaclass.dispatchers,
                    cube.metaclass.decorators,
                )(cube.content)
            else:
                self.scheduler.schedule(
                    cube.metaclass.timer,
                    cube.metaclass.cancelable,
                    cube.metaclass.dispatchers,
                    cube.metaclass.decorators,
                )(cube.content)
        else:
            return

        return True

    def uninstall(self, cube: Cube) -> Any:
        if isinstance(cube.metaclass, SchedulerSchema):
            def filterTagTask(item):
                if not hasattr(cube, 'tag'):
                    return False
                if not hasattr(item, 'tag'):
                    return False
                return item.tag == cube.tag

            def filterNormal(item):
                return item.target is cube.content
            if hasattr(cube, 'tag'):
                filter_fun = filterTagTask
            else:
                filter_fun = filterNormal
            target_tasks = list(
                filter(
                    lambda x: filter_fun(x), self.scheduler.schedule_tasks
                )
            )
            if target_tasks:
                target = target_tasks[0]
                target.stop_gen_interval()
                target.stop()
                self.scheduler.schedule_tasks.remove(target)
        else:
            return

        return True
