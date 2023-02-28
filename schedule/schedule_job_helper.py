from graia.saya import Saya
from graia.scheduler.saya import SchedulerSchema
from graia.saya.cube import Cube

from graia.scheduler.timers import crontabify

from config import ScheduleTask
from schedule.JobNameDispatcher import JobNameDispatcher


class ScheduleJobHelper:

    def __init__(self, channel):
        self.channel = channel
        self.saya = Saya.current()
        self.cubeMap = {}

    def addScheduleJob(self, schedule_task: ScheduleTask, job_callback):
        cube = Cube(job_callback, self.__getSchemaByRules(schedule_task))
        cube.tag = schedule_task.name
        if schedule_task.name in self.cubeMap.keys():
            print(f"schedule job [{schedule_task.name}] already add,replace new one.")
            self.removeJob(schedule_task.name)
        self.cubeMap[schedule_task.name] = cube
        self.channel.content.append(cube)
        with self.saya.behaviour_interface.require_context(self.channel.module) as interface:
            interface.allocate_cube(cube)

    def removeScheduleJob(self, job_name):
        target_cube = self.cubeMap.pop(job_name)
        if target_cube:
            self.channel.cancel(target_cube.content)
            with self.saya.behaviour_interface.require_context(self.channel.module) as interface:
                interface.uninstall_cube(target_cube)

    def removeAllJob(self):
        for k in list(self.cubeMap.keys()):
            target_cube = self.cubeMap.pop(k)
            if target_cube:
                self.channel.cancel(target_cube.content)
                with self.saya.behaviour_interface.require_context(self.channel.module) as interface:
                    interface.uninstall_cube(target_cube)

    def removeJob(self, job_name):
        if job_name not in self.cubeMap.keys():
            return
        target_cube = self.cubeMap.pop(job_name)
        if target_cube:
            self.channel.cancel(target_cube.content)
            with self.saya.behaviour_interface.require_context(self.channel.module) as interface:
                interface.uninstall_cube(target_cube)

    def __getSchemaByRules(self, schedule_task: ScheduleTask):
        return SchedulerSchema(
            crontabify(schedule_task.rule),
            cancelable=True,
            dispatchers=[JobNameDispatcher(schedule_task)]
        )
