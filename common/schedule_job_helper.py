from graia.saya import Cube, Saya
from graia.scheduler.saya import SchedulerSchema

from graia.scheduler.timers import crontabify


class ScheduleJobHelper:

    def __init__(self, channel):
        self.channel = channel
        self.saya = Saya.current()
        self.cubeMap = {}

    def addScheduleJob(self, job_name, job_callback, schedule_rules):
        cube = Cube(job_callback, self.__getSchemaByRules(schedule_rules))
        if job_name in self.cubeMap.keys():
            print(f"schedule job [{job_name}] already add.")
            return
        self.cubeMap[job_name] = cube
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

    def __getSchemaByRules(self, schedule_rules):
        return SchedulerSchema(
            crontabify(schedule_rules),
            cancelable=True
        )


