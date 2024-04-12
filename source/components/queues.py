from faststream.rabbit import RabbitQueue
from config import DOCUMENT_QUEUE


document_queue = RabbitQueue(name=DOCUMENT_QUEUE)  # , robust=False, durable=True)
