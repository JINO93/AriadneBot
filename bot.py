import asyncio
import os

from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour

from schedule.TagGraiaScheduler import TagGraiaScheduler
from schedule.TagGraiaSchedulerBehaviour import TagGraiaSchedulerBehaviour

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="jino_ser",  # 填入 verifyKey
        account=1834240938,  # 你的机器人的 qq 号
    )
)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
# 定时任务
scheduler = TagGraiaScheduler(loop, bcc)
saya.install_behaviours(TagGraiaSchedulerBehaviour(scheduler))

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
    for module in os.listdir("modules"):
        if module in ignore:
            continue
        try:
            if os.path.isdir(module):
                saya.require(f"modules.{module}")
            else:
                saya.require(f"modules.{module.split('.')[0]}")
        except ModuleNotFoundError:
            pass

if __name__ == "__main__":
    try:
        loop.run_until_complete(app.lifecycle())
    except KeyboardInterrupt:
        print('----start exiting---')
        loop.run_until_complete(app.request_stop())
