from os import environ


RABBITMQ_URL = environ['RABBITMQ_URL']

DECLARATION_QUEUE = "declaration_queue"

EXCEL_TEMPLATE_PATH = '../declaration_template.xlsx'

JWT_SECRET = environ["JWT_SECRET"]

TEST_USER_ID = "01HRY2SVSPZN4VABH90S4VFZ7H"

CONTENT_API_URL = environ["CONTENT_API_URL"]
