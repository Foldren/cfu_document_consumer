from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from faststream.rabbit import RabbitRouter
from openpyxl.reader.excel import load_workbook
from components.intervals import AP_ROW_INTERVALS
from components.decorators import consumer
from components.enums import DocumentTypeEnum
from components.queues import document_queue
from components.requests.advance_payment import CreateAdvancePaymentRequest
from components.responses.advance_payment import CreateAdvancePaymentResponse
from config import IS_THIS_LOCAL, EXCEL_AP_TEMPLATE_PATH
from db_models.document import Document, DocumentStatus
from modules.content_api import ContentApi
from modules.excel import Excel
from modules.xml import XML

router = RabbitRouter()


@consumer(router=router, queue=document_queue, pattern="document.create-advance-payment",
          request=CreateAdvancePaymentRequest)
async def create_advance_payment(request: CreateAdvancePaymentRequest) -> CreateAdvancePaymentResponse:
    """
    Роут на создание авансового платежа. Добавляет поля в шаблон
    advance_payment.xml, advance_payment.xlsx, сохраняет файл в поток в байтах и сохраняет в контентном мс.
    :param request: объект на создание авансового платежа CreateAdvancePaymentRequest
    :return: response объект на создание авансового платежа CreateAdvancePaymentResponse
    """

    current_date = datetime.now()
    patronymic = "" if request.owner.patronymic is None else f"_{request.owner.patronymic}"
    file_name = (f"{request.owner.lastName}_{request.owner.firstName}{patronymic}-{request.advancePaymentData.inn}-"
                 f"{current_date.strftime('%Y-%m-%d')}")

    # Создаем декларацию, указываем статус proccess по умолчанию
    advance_payment = await Document.create(
        user_id=request.userID,
        file_name=file_name,
        date=current_date,
        legal_entity_inn=request.advancePaymentData.inn,
        legal_entity_id=request.advancePaymentData.legalEntityID,
        type=DocumentTypeEnum.advance_payment
    )

    # Генерим xml файл -------------------------------------------------------------------------------------------------
    xml_bytes = await XML.form_xml_bytes_advance_payment_file(inn=request.advancePaymentData.inn,
                                                              last_name=request.owner.lastName,
                                                              first_name=request.owner.firstName,
                                                              patronymic=request.owner.patronymic,
                                                              report_year=request.advancePaymentData.reportingYear,
                                                              authority_code=request.advancePaymentData.authorityCode,
                                                              octmo_code=request.advancePaymentData.oktmo,
                                                              kbk=request.advancePaymentData.kbk,
                                                              quarter=request.advancePaymentData.quarter,
                                                              revenue=request.advancePaymentData.revenue)

    # Фомируем xlsx файл -----------------------------------------------------------------------------------------------
    wb = load_workbook(filename=EXCEL_AP_TEMPLATE_PATH)
    xlsx_stream = BytesIO()

    list_name = 'Лист 1'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        {'text': request.advancePaymentData.authorityCode, 'interval': AP_ROW_INTERVALS[list_name]['TAX_CODE']},
        {'text': request.owner.lastName, 'interval': AP_ROW_INTERVALS[list_name]['LAST_NAME']},
        {'text': request.owner.firstName, 'interval': AP_ROW_INTERVALS[list_name]['FIRST_NAME']},
        {'text': request.owner.patronymic, 'interval': AP_ROW_INTERVALS[list_name]['PATRONYMIC']},
    ])

    # Форматируем сумму платежа с дефисом
    revenue = ""
    for i in range(14):
        if i > (14 - len(str(request.advancePaymentData.revenue))):
            revenue += str(request.advancePaymentData.revenue)
            break
        else:
            revenue += "-"

    list_name = 'Лист 2'
    await Excel(worksh=wb[list_name]).insert_rows_to_ws([
        {'text': request.advancePaymentData.oktmo,
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['OCTMO_CODE']},
        {'text': request.advancePaymentData.kbk,
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['KBK']},
        {'text': revenue,
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['REVENUE']},
        {'text': 34,
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['Q_CODE']},
        {'text': '0' + str(request.advancePaymentData.quarter),
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['QUARTER']},
        {'text': request.advancePaymentData.reportingYear,
         'interval': AP_ROW_INTERVALS[list_name]['QUARTERS'][request.advancePaymentData.quarter]['REPORT_YEAR']},
    ])

    # Записываем данные в потоки ---------------------------------------------------------------------------------------
    xml_stream = BytesIO(xml_bytes)
    wb.save(xlsx_stream)

    # Сохраняем тестовый файл ------------------------------------------------------------------------------------------
    if IS_THIS_LOCAL:
        with open("test_advance_payment.xml", "wb") as f:
            f.write(xml_stream.getvalue())

        with open("test_advance_payment.xlsx", "wb") as f:
            f.write(xlsx_stream.getvalue())

    try:
        # Загружаем в контентный микросервис файл xlsx
        xlsx_content_resp = await ContentApi(user_id=request.userID).upload(data=xlsx_stream.getvalue(),
                                                                            file_name=f"{file_name}.xlsx")

        # Загружаем в контентный микросервис файл xml
        xml_content_resp = await ContentApi(user_id=request.userID).upload(data=xml_stream.getvalue(),
                                                                           file_name=f"{file_name}.xml")

        advance_payment.status = DocumentStatus.success
        advance_payment.xlsx_image_url = xlsx_content_resp.fileName
        advance_payment.xml_image_url = xml_content_resp.fileName

        await advance_payment.save()

    # В случае если не сработал nginx или vpn
    except JSONDecodeError:
        advance_payment.status = DocumentStatus.error
        await advance_payment.save()
        raise Exception("Ошибка подключения 403, (контентный микросервис).")

    # В случае ошибки со стороны контентного мс
    except Exception as e:
        advance_payment.status = DocumentStatus.error
        await advance_payment.save()
        raise Exception(e)

    return CreateAdvancePaymentResponse(advancePaymentID=advance_payment.id)
