import threading
from typing import TypeVar

from tinydb import TinyDB, where

from config.model import GlobalConfig, ModuleConfig, ScheduleTask

T = TypeVar("T", None, ModuleConfig)


class ConfigManager:
    _instance_lock = threading.Lock()

    def __init__(self, config_file_path):
        print("__init__")
        self._db = TinyDB(config_file_path)
        # self._global_config_table = self._db.table('global_config')
        self._module_config_table = self._db.table('module_config')
        self._user_config_table = self._db.table('user_config')
        self._schedule_task_table = self._db.table('schedule_task')
        # self._global_config = self._getOrInitGlobalConfig()
        # self._module_config = self._getOrInitModuleConfig()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ConfigManager, '_instance'):
            with ConfigManager._instance_lock:
                if not hasattr(ConfigManager, '_instance'):
                    ConfigManager._instance = object.__new__(cls)
        return ConfigManager._instance

    # def _getOrInitGlobalConfig(self):
    #     config_content = self._global_config_table.all()
    #     if not config_content or len(config_content) <= 0:
    #         g_config = GlobalConfig(module_config=[])
    #         print("init global config")
    #         self._global_config_table.upsert(g_config.dict(), where('module_config').exists())
    #     else:
    #         g_config = GlobalConfig(**config_content[0])
    #     return g_config

    # def saveGlobalConfig(self):
    #     print("save global config")
    #     # print(self)
    #     config_dict = self._global_config.dict()
    #     self._global_config_table.upsert(config_dict, where('module_config').exists())

    # def _getOrInitModuleConfig(self):
    #     config_content = self._module_config_table.all()
    #     if not config_content or len(config_content) <= 0:
    #         g_config = GlobalConfig(module_config=[])
    #         print("init global config")
    #         self._module_config_table.upsert(g_config.dict(), where('module_config').exists())
    #     else:
    #         g_config = GlobalConfig(**config_content[0])
    #     return g_config

    def getModuleConfig(self, moduleName, cls=ModuleConfig):
        target_module = self._module_config_table.search(where('name') == moduleName)
        # match_res = list(filter(lambda x: x['name'] == moduleName, self._global_config.module_config))
        if target_module:
            target_module = cls(**target_module[0])
        else:
            target_module = cls(name=moduleName)
            self._module_config_table.insert(target_module.dict())
        return target_module

    def updateModuleConfig(self, moduleConfig):
        config_dict = moduleConfig.dict()
        self._module_config_table.update(config_dict, where('name') == moduleConfig.name)

    def addOrUpdateScheduleTask(self, scheduleTask):
        self._schedule_task_table.upsert(scheduleTask.dict(), where('name') == scheduleTask.name)

    def deleteScheduleTask(self, scheduleTask):
        self._schedule_task_table.remove(scheduleTask.dict(), where('name') == scheduleTask.name)

    def getScheduleTask(self, task_name):
        target_task = self._schedule_task_table.search(where('name') == task_name)
        if target_task:
            return ScheduleTask(**target_task[0])

    def getScheduleTasksByModule(self, module_name):
        target_tasks = self._schedule_task_table.search(where('module') == module_name)
        if target_tasks:
            return list(map(lambda x: ScheduleTask(**x), target_tasks))