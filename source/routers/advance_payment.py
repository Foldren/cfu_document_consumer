from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from faststream.rabbit import RabbitRouter
from components.decorators import consumer
from components.queues import document_queue
from components.requests.advance_payment import CreateAdvancePaymentRequest
from components.responses.advance_payment import CreateAdvancePaymentResponse
from config import IS_THIS_LOCAL
from db_models.document import Document, DocumentStatus
from modules.content_api import ContentApi
from modules.xml import XML

router = RabbitRouter()


@consumer(router=router, queue=document_queue, pattern="document.create-advance-payment",
          request=CreateAdvancePaymentRequest)
async def create_advance_payment(request: CreateAdvancePaymentRequest) -> CreateAdvancePaymentResponse:
    """
    Роут на создание авансового платежа. Добавляет поля в шаблон
    advance_payment.xml, сохраняет файл в поток в байтах и сохраняет в контентном мс.
    :param request: объект на создание авансового платежа CreateAdvancePaymentRequest
    :return: response объект на создание авансового платежа CreateAdvancePaymentResponse
    """

    current_date = datetime.now()

    # Создаем декларацию, указываем статус proccess по умолчанию
    advance_payment = await Document.create(
        user_id=request.userID,
        date=current_date,
        legal_entity_inn=request.advancePayment.inn,
        legal_entity_id=request.advancePayment.legalEntityID
    )

    # Генерим xml файл
    xml_file_name = (
        f"{request.owner.lastName}_{request.owner.firstName}_{request.owner.patronymic}-{request.advancePayment.inn}-"
        f"{current_date.strftime('%Y-%m-%d')}.xml")  # Имя файла fio-inn-date

    xml_bytes = await XML.form_xml_bytes_advance_payment_file(inn=request.advancePayment.inn,
                                                              last_name=request.owner.lastName,
                                                              first_name=request.owner.firstName,
                                                              patronymic=request.owner.patronymic,
                                                              report_year=request.advancePayment.reportingYear,
                                                              authority_code=request.advancePayment.authorityCode,
                                                              octmo_code=request.advancePayment.oktmo,
                                                              kbk=request.advancePayment.kbk,
                                                              quarter=request.advancePayment.quarter,
                                                              revenue=request.advancePayment.revenue)
    xml_stream = BytesIO(xml_bytes)

    # Сохраняем тестовый файл
    if IS_THIS_LOCAL:
        with open("test_advance_payment.xml", "wb") as f:
            f.write(xml_stream.getvalue())

    try:
        # Загружаем в контентный микросервис файл xml
        xml_content_resp = await ContentApi(user_id=request.userID).upload(data=xml_stream.getvalue(),
                                                                           file_name=xml_file_name)

        advance_payment.status = DocumentStatus.success
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
