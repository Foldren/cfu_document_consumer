from faststream.rabbit import RabbitRouter

router = RabbitRouter()


# @router.subscriber(queue=tg_bank_queue)
# async def purge_messages():
#     pass
