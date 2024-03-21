from faststream.rabbit import RabbitQueue
from config import DECLARATION_QUEUE


declaration_queue = RabbitQueue(name=DECLARATION_QUEUE)  # , robust=False, durable=True)
