from enum import IntEnum
from typing import List

from pydantic import BaseModel


class ScheduleTask(BaseModel):
    name: str
    rule: str
    command: str
    enable: bool = True
    subscribe_user: List[int] = []
    subscribe_group: List[int] = []


class ModuleConfig(BaseModel):
    name: str
    enable: bool = True
    super_user: int = -1
    # schedule_tasks: List[ScheduleTask] = []


class IdType(IntEnum):
    QQ_ID = 1
    GROUP_ID = 2


class UserConfig(BaseModel):
    id: int
    type: IdType
    block_list: List[str] = []


class GlobalConfig(BaseModel):
    module_config: List[dict] = []
