import os 

import asgi
from workers import WorkerEntrypoint

from main import app

class Default(WorkerEntrypoint):
    
    async def fetch(self, request):    
        if self.env:
            os.environ.update({k: v for k, v in self.env.to_py().items() if isinstance(v, str)})
        return await asgi.fetch(app, request, self.env)
