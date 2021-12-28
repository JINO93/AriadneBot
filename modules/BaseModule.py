from graia.saya import Channel, SayaModuleInstalled, SayaModuleUninstall, BaseSchema
from graia.saya.builtins.broadcast import ListenerSchema

from config import ModuleConfig
from config.config import global_config_manager
from schedule.schedule_job_helper import ScheduleJobHelper


class BaseModule:
    name: str
    channel: Channel
    schedule_helper: ScheduleJobHelper
    module_config: ModuleConfig

    def __init__(self, channel: Channel, module_name, module_description, module_author):
        self.channel = channel
        self.name = channel.module

        self.channel.name(module_name)
        self.channel.description(module_description)
        self.channel.author(module_author)

        self.schedule_helper = ScheduleJobHelper(channel)
        self.module_config = global_config_manager.getModuleConfig(channel.module)

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

        # schedule_tasks = global_config_manager.getScheduleTasksByModule(channel.module)
        # if schedule_tasks:
        #     for task in schedule_tasks:
        #         print(f'开启定时任务【{task.name}】,规则为：{task.rule}')
        #         self.schedule_helper.addScheduleJob(task.name, schedule_send_pic, task.rule)

        self.init_module()

    def use(self, schema: BaseSchema):
        return self.channel.use(schema)

    def init_module(self):
        pass
