from graia.broadcast import DispatcherInterface
from graia.broadcast.entities.dispatcher import BaseDispatcher


class JobNameDispatcher(BaseDispatcher):

    def __init__(self, job_name):
        self.job_name = job_name

    async def catch(self, interface: DispatcherInterface):
        if interface.name == 'job_name':
            return self.job_name
        return None
