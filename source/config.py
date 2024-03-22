from os import environ, getcwd
from dotenv import load_dotenv


load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(getcwd())

RABBITMQ_URL = environ['RABBITMQ_URL']

DECLARATION_QUEUE = "declaration_queue"

EXCEL_TEMPLATE_PATH = str(getcwd()) + "/declaration_template.xlsx"

JWT_SECRET = environ["JWT_SECRET"]

TEST_USER_ID = "01HRY2SVSPZN4VABH90S4VFZ7H"

CONTENT_API_URL = environ["CONTENT_API_URL"]

TORTOISE_CONFIG = {
    "connections": {
        "declaration": environ['DC_PG_URL'],
    },
    "apps": {
        "declaration": {"models": ["db_models.declaration", "aerich.models"], "default_connection": "declaration"},
    }
}
