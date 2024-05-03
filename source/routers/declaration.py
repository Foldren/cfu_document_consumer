from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from faststream.rabbit import RabbitRouter
from openpyxl.reader.excel import load_workbook
from components.intervals import DECL_INTERVALS
from components.decorators import consumer
from components.queues import document_queue
from components.requests.declaration import CreateDeclarationRequest
from components.responses.declaration import CreateDeclarationResponse
from config import EXCEL_DECL_TEMPLATE_PATH, IS_THIS_LOCAL
from db_models.document import Document, DocumentStatus
from modules.content_api import ContentApi
from modules.excel import Excel
from modules.formula import Formula
from modules.xml import XML

router = RabbitRouter()


@consumer(router=router, queue=document_queue, pattern="document.create-declaration",
          request=CreateDeclarationRequest)
async def create_declaration(request: CreateDeclarationRequest) -> CreateDeclarationResponse:
    """
    Роут на создание декларации. Подсчитывает значения полей декларации, добавляет их в шаблоны
    declaration_template.xlsx, declaration_template.xml, сохраняет файлы в поток в байтах и сохраняет в контентном мс.
    :param request: объект на создание декларации CreateDeclarationRequest
    :return: response объект на создание декларации CreateDeclarationResponse
    """

    current_date = datetime.now()
    patronymic = "" if request.owner.patronymic is None else f"_{request.owner.patronymic}"
    file_name = (f"{request.owner.lastName}_{request.owner.firstName}{patronymic}-{request.base.inn}-"
                 f"{current_date.strftime('%Y-%m-%d')}")

    # Создаем декларацию, указываем статус proccess по умолчанию
    declaration = await Document.create(
        user_id=request.userID,
        file_name=file_name,
        date=current_date,
        legal_entity_inn=request.base.inn,
        legal_entity_id=request.base.legalEntityID
    )

    xlsx_stream = BytesIO()
    wb = load_workbook(filename=EXCEL_DECL_TEMPLATE_PATH)
    date_ip_open = datetime.strptime(request.base.createDate, '%Y-%m-%d')

    formula = Formula(rate=request.base.rate,
                      report_year=int(request.declaration.reportingYear),
                      year_ip_open=date_ip_open.year,
                      month_ip_open=date_ip_open.month,
                      day_ip_open=date_ip_open.day,
                      cells_110_to_113=[request.revenue.threeMonths, request.revenue.sixMonths,
                                        request.revenue.nineMonths, request.revenue.twelveMonths],
                      workers_count=request.base.employeesCount
                      )

    codes = await formula.get_codes()

    list_name = 'Титул'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        # Вставляем ИНН
        {'text': request.base.inn, 'interval': DECL_INTERVALS[list_name]['INN']},
        # Вставляем отчетный год
        {'text': request.declaration.reportingYear, 'interval': DECL_INTERVALS[list_name]['REPORT_YEAR']},
        # Вставляем Код налоговой инспекции
        {'text': request.declaration.authorityCode, 'interval': DECL_INTERVALS[list_name]['TAX_INSPECTION_CODE']},
        # Вставляем Фамилию
        {'text': request.owner.lastName, 'interval': DECL_INTERVALS[list_name]['LAST_NAME']},
        # Вставляем Имя
        {'text': request.owner.firstName, 'interval': DECL_INTERVALS[list_name]['FIRST_NAME']},
        # Вставляем Отчество
        {'text': request.owner.patronymic, 'interval': DECL_INTERVALS[list_name]['PATRONYMIC']},
        # Вставляем Мобильный номер
        {'text': request.owner.phoneNumber, 'interval': DECL_INTERVALS[list_name]['PHONE_NUMBER']},
        # Вставляем Фамилию налогоплатильщика
        {'text': request.owner.lastName, 'interval': DECL_INTERVALS[list_name]['TAX_LAST_NAME']},
        # Вставляем Имя налогоплатильщика
        {'text': request.owner.firstName, 'interval': DECL_INTERVALS[list_name]['TAX_FIRST_NAME']},
        # Вставляем Отчество налогоплатильщика
        {'text': request.owner.patronymic, 'interval': DECL_INTERVALS[list_name]['TAX_PATRONYMIC']},
        # Вставляем ИП налогоплатильщика
        {'text': request.owner.taxPayer.split("\\n")[1], 'interval': DECL_INTERVALS[list_name]['TAX_IP']},
    ])

    list_name = 'Раздел 1.1'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        # Вставляем ОКТМО код
        {'text': request.declaration.oktmoCurrent, 'interval': DECL_INTERVALS[list_name]['OKTMO_010']},
        # Вставляем строку 020
        {'text': codes['020'], 'interval': DECL_INTERVALS[list_name]['020']},
        # Вставляем строку 040
        {'text': codes['040'], 'interval': DECL_INTERVALS[list_name]['040']},
        # Вставляем строку 050
        {'text': abs(codes['050']), 'interval': DECL_INTERVALS[list_name]['050']},
        # Вставляем строку 050
        {'text': codes['070'], 'interval': DECL_INTERVALS[list_name]['070']},
        # Вставляем строку 050
        {'text': abs(codes['080']), 'interval': DECL_INTERVALS[list_name]['080']},
        # Вставляем строку 100
        {'text': codes['100'], 'interval': DECL_INTERVALS[list_name]['100']},
        # Вставляем строку 101
        {'text': codes['101'], 'interval': DECL_INTERVALS[list_name]['101']},
        # Вставляем строку 110
        {'text': abs(codes['1_110']), 'interval': DECL_INTERVALS[list_name]['110']},
    ])

    list_name = 'Раздел 2.1.1'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        # Вставляем строку 101 (налоговая ставка)
        {'text': request.base.rate, 'interval': DECL_INTERVALS[list_name]['101']},
        # Вставляем строку 110
        {'text': codes['2_110'], 'interval': DECL_INTERVALS[list_name]['110']},
        # Вставляем строку 111
        {'text': codes['111'], 'interval': DECL_INTERVALS[list_name]['111']},
        # Вставляем строку 112
        {'text': codes['112'], 'interval': DECL_INTERVALS[list_name]['112']},
        # Вставляем строку 113
        {'text': codes['113'], 'interval': DECL_INTERVALS[list_name]['113']},
        # Вставляем строку 120 (налоговая ставка)
        {'text': codes['120'], 'interval': DECL_INTERVALS[list_name]['120']},
        # Вставляем строку 121 (налоговая ставка)
        {'text': codes['121'], 'interval': DECL_INTERVALS[list_name]['121']},
        # Вставляем строку 122 (налоговая ставка)
        {'text': codes['122'], 'interval': DECL_INTERVALS[list_name]['122']},
        # Вставляем строку 123 (налоговая ставка)
        {'text': codes['123'], 'interval': DECL_INTERVALS[list_name]['123']},
        # Вставляем строку 130
        {'text': codes['130'], 'interval': DECL_INTERVALS[list_name]['130']},
        # Вставляем строку 131
        {'text': codes['131'], 'interval': DECL_INTERVALS[list_name]['131']},
        # Вставляем строку 132
        {'text': codes['132'], 'interval': DECL_INTERVALS[list_name]['132']},
        # Вставляем строку 133
        {'text': codes['133'], 'interval': DECL_INTERVALS[list_name]['133']},
    ])

    list_name = 'Раздел 2.1.1 (продолжение)'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        # Вставляем строку 140
        {'text': codes['140'], 'interval': DECL_INTERVALS[list_name]['140']},
        # Вставляем строку 141
        {'text': codes['141'], 'interval': DECL_INTERVALS[list_name]['141']},
        # Вставляем строку 142
        {'text': codes['142'], 'interval': DECL_INTERVALS[list_name]['142']},
        # Вставляем строку 143
        {'text': codes['143'], 'interval': DECL_INTERVALS[list_name]['143']},
    ])

    # Сохраняем в поток
    wb.save(xlsx_stream)

    # Генерим xml файл
    xml_bytes = await XML.form_xml_bytes_declaration_file(inn=request.base.inn, last_name=request.owner.lastName,
                                                          first_name=request.owner.firstName,
                                                          patronymic=request.owner.patronymic,
                                                          report_year=request.declaration.reportingYear,
                                                          authority_code=request.declaration.authorityCode,
                                                          octmo_code=request.declaration.oktmoCurrent, rate=request.base.rate,
                                                          workers_count=request.base.employeesCount,
                                                          phone_number=request.owner.phoneNumber,
                                                          codes=codes)
    xml_stream = BytesIO(xml_bytes)

    # Сохраняем тестовый файл
    if IS_THIS_LOCAL:
        with open("test_declaration.xlsx", "wb") as f:
            f.write(xlsx_stream.getvalue())
        with open("test_declaration.xml", "wb") as f:
            f.write(xml_stream.getvalue())

    try:
        # Загружаем в контентный микросервис файл xlsx
        xlsx_content_resp = await ContentApi(user_id=request.userID).upload(data=xlsx_stream.getvalue(),
                                                                            file_name=f"{file_name}.xlsx")

        # Загружаем в контентный микросервис файл xml
        xml_content_resp = await ContentApi(user_id=request.userID).upload(data=xml_stream.getvalue(),
                                                                           file_name=f"{file_name}.xml")

        declaration.status = DocumentStatus.success
        declaration.xlsx_image_url = xlsx_content_resp.fileName
        declaration.xml_image_url = xml_content_resp.fileName

        await declaration.save()

    # В случае если не сработал nginx или vpn
    except JSONDecodeError:
        declaration.status = DocumentStatus.error
        await declaration.save()
        raise Exception("Ошибка подключения 403, (контентный микросервис).")

    # В случае ошибки со стороны контентного мс
    except Exception as e:
        declaration.status = DocumentStatus.error
        await declaration.save()
        raise Exception(e)

    return CreateDeclarationResponse(declarationID=declaration.id)
