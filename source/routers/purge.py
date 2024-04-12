from faststream.rabbit import RabbitRouter
from components.queues import document_queue

router = RabbitRouter()


# @router.subscriber(queue=document_queue)
# async def purge_messages():
#     pass
