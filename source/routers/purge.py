from faststream.rabbit import RabbitRouter
from components.queues import declaration_queue

router = RabbitRouter()


# @router.subscriber(queue=declaration_queue)
# async def purge_messages():
#     pass
