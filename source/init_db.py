from tortoise import Tortoise
from config import TORTOISE_CONFIG


async def init_db():
    await Tortoise.init(TORTOISE_CONFIG)
    await Tortoise.generate_schemas(safe=True)

    # if date(2024, 2, 22) == date.today():
    #     command = Command(tortoise_config=TORTOISE_CONFIG, app='declaration', location="./migrations")
    #     await command.init()
    #     await command.upgrade(True)