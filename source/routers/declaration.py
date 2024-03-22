from datetime import datetime
from io import BytesIO
from faststream.rabbit import RabbitRouter
from openpyxl.reader.excel import load_workbook
from components.declaration_fields import ROW_OPTIONS
from components.decorators import consumer
from components.queues import declaration_queue
from components.requests.declaration import CreateDeclarationRequest, GetDeclarationsRequest
from components.responses.children import CDeclaration
from components.responses.declaration import CreateDeclarationResponse, GetDeclarationsResponse
from config import EXCEL_TEMPLATE_PATH
from db_models.declaration import Declaration, DeclarationStatus
from modules.content_api import ContentApi
from modules.excel import Excel

router = RabbitRouter()


@consumer(router=router, queue=declaration_queue, pattern="declaration.create-declaration",
          request=CreateDeclarationRequest)
async def create_declaration(request: CreateDeclarationRequest):
    current_date = datetime.now()
    file_name = (f"{request.owner.lastName}_{request.owner.firstName}_{request.owner.patronymic}-{request.base.inn}-"
                 f"{current_date.strftime('%Y-%m-%d')}.xlsx")  # Имя файла fio-inn-date

    # Создаем декларацию, указываем статус proccess по умолчанию
    declaration = await Declaration.create(
        user_id=request.userID,
        file_name=file_name,
        date=current_date,
        legal_entity_inn=request.base.inn,
        legal_entity_id=request.base.legalEntityID
    )

    output = BytesIO()
    wb = load_workbook(filename=EXCEL_TEMPLATE_PATH)

    code_110 = request.revenue.threeMonths
    code_111 = request.revenue.sixMonths
    code_112 = request.revenue.nineMonths
    code_113 = request.revenue.twelveMonths

    code_120 = request.base.rate
    code_121 = request.base.rate
    code_122 = request.base.rate
    code_123 = request.base.rate

    code_130 = (code_120 * code_110) // 100
    code_131 = (code_121 * code_111) // 100
    code_132 = (code_122 * code_112) // 100
    code_133 = (code_123 * code_113) // 100

    ws = wb['Титул']  # Открываем лист 'Титул'
    await Excel(worksh=ws).insert_rows_to_ws([
        # Вставляем ИНН
        {'text': request.base.inn, 'row_options': ROW_OPTIONS['TITLE']['INN']},
        # Вставляем отчетный год
        {'text': request.declaration.reportingYear, 'row_options': ROW_OPTIONS['TITLE']['REPORT_YEAR']},
        # Вставляем Код налоговой инспекции
        {'text': request.declaration.authorityCode, 'row_options': ROW_OPTIONS['TITLE']['TAX_INSPECTION_CODE']},
        # Вставляем Фамилию
        {'text': request.owner.lastName, 'row_options': ROW_OPTIONS['TITLE']['LAST_NAME']},
        # Вставляем Имя
        {'text': request.owner.firstName, 'row_options': ROW_OPTIONS['TITLE']['FIRST_NAME']},
        # Вставляем Отчество
        {'text': request.owner.patronymic, 'row_options': ROW_OPTIONS['TITLE']['PATRONYMIC']},
        # Вставляем Отчество
        {'text': request.owner.phoneNumber, 'row_options': ROW_OPTIONS['TITLE']['PHONE_NUMBER']},
    ], is_title_list=True)

    ws = wb['Раздел 1.1']  # Открываем лист 'Раздел 1.1'
    await Excel(worksh=ws).insert_rows_to_ws([
        # Вставляем ОКТМО код
        {'text': request.declaration.oktmoCurrent, 'row_options': ROW_OPTIONS['1_1']['OKTMO_010']},
    ])

    ws = wb['Раздел 2.1.1']  # Открываем лист 'Раздел 2.1.1'
    await Excel(worksh=ws).insert_rows_to_ws([
        # Вставляем строку 101 (налоговая ставка)
        {'text': request.base.rate, 'row_options': ROW_OPTIONS['2_1_1']['101']},
        # Вставляем строку 110
        {'text': code_110, 'row_options': ROW_OPTIONS['2_1_1']['110']},
        # Вставляем строку 111
        {'text': code_111, 'row_options': ROW_OPTIONS['2_1_1']['111']},
        # Вставляем строку 112
        {'text': code_112, 'row_options': ROW_OPTIONS['2_1_1']['112']},
        # Вставляем строку 113
        {'text': code_113, 'row_options': ROW_OPTIONS['2_1_1']['113']},
        # Вставляем строку 120 (налоговая ставка)
        {'text': request.base.rate, 'row_options': ROW_OPTIONS['2_1_1']['120']},
        # Вставляем строку 121 (налоговая ставка)
        {'text': request.base.rate, 'row_options': ROW_OPTIONS['2_1_1']['121']},
        # Вставляем строку 122 (налоговая ставка)
        {'text': request.base.rate, 'row_options': ROW_OPTIONS['2_1_1']['122']},
        # Вставляем строку 123 (налоговая ставка)
        {'text': request.base.rate, 'row_options': ROW_OPTIONS['2_1_1']['123']},
        # Вставляем строку 130
        {'text': code_130, 'row_options': ROW_OPTIONS['2_1_1']['130']},
        # Вставляем строку 131
        {'text': code_131, 'row_options': ROW_OPTIONS['2_1_1']['131']},
        # Вставляем строку 132
        {'text': code_132, 'row_options': ROW_OPTIONS['2_1_1']['132']},
        # Вставляем строку 133
        {'text': code_133, 'row_options': ROW_OPTIONS['2_1_1']['133']},
    ])

    try:
        # Сохраняем в поток
        wb.save(output)

        # Загружаем в контентный микросервис файл
        content_response = await ContentApi(user_id=request.userID).upload(data=output.getvalue(), file_name=file_name)

        declaration.status = DeclarationStatus.success
        declaration.image_url = content_response.fileName
        await declaration.save()

    except Exception:
        declaration.status = DeclarationStatus.error

    return CreateDeclarationResponse(declarationID=declaration.id)


@consumer(router=router, queue=declaration_queue, pattern="declaration.get-declaration-list",
          request=GetDeclarationsRequest)
async def get_declaration_list(request: GetDeclarationsRequest) -> GetDeclarationsResponse:
    declarations = await Declaration.filter(user_id=request.userID).all()

    lit_declarations_r = []
    for dclr in declarations:
        lit_declarations_r.append(CDeclaration(name=dclr.file_name,
                                               inn=dclr.legal_entity_inn,
                                               date=dclr.date.strftime('%Y-%m-%d'),
                                               status=dclr.status,
                                               url=dclr.image_url
                                               ))

    return GetDeclarationsResponse(declarations=lit_declarations_r)
