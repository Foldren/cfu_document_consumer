from os import environ, getcwd
from dotenv import load_dotenv


load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(getcwd())

RABBITMQ_URL = environ['RABBITMQ_URL']

DOCUMENT_QUEUE = "document_queue"

EXCEL_DECL_TEMPLATE_PATH = str(getcwd()) + "/declaration_template.xlsx"

EXCEL_AP_TEMPLATE_PATH = str(getcwd()) + "/advance_payment_template.xlsx"

JWT_SECRET = environ["JWT_SECRET"]

TEST_USER_ID = "01HRY2SVSPZN4VABH90S4VFZ7H"

CONTENT_API_URL = environ["CONTENT_API_URL"]

TORTOISE_CONFIG = {
    "connections": {
        "document": environ['DC_PG_URL'],
    },
    "apps": {
        "document": {"models": ["db_models.document", "aerich.models"], "default_connection": "document"},
    }
}
