from asyncio import run
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from config import RABBITMQ_URL
from routers import declaration, purge


broker = RabbitBroker(RABBITMQ_URL)
app = FastStream(broker)

broker.include_routers(purge.router, declaration.router)


async def main():
    await app.run()


if __name__ == "__main__":
    run(main())
