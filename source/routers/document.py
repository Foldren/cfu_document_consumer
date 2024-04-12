from faststream.rabbit import RabbitRouter
from components.decorators import consumer
from components.queues import document_queue
from components.requests.document import GetDocumentsRequest, RemoveDocumentRequest
from components.responses.children import CDocument
from components.responses.document import GetDocumentsResponse, RemoveDocumentResponse
from db_models.document import Document
from modules.content_api import ContentApi

router = RabbitRouter()


@consumer(router=router, queue=document_queue, pattern="document.get-document-list",
          request=GetDocumentsRequest)
async def get_document_list(request: GetDocumentsRequest) -> GetDocumentsResponse:
    """
    Роут на получение списка документов из бд.
    :param request: объект на получение списка документов GetDocumentsRequest
    :return: response объект на получение списка документов GetDocumentsResponse
    """

    documents = await Document.filter(user_id=request.userID, status__not='no_file').all()

    list_documents_r = []
    for doc in documents:
        list_documents_r.append(CDocument(id=doc.id,
                                         inn=doc.legal_entity_inn,
                                         date=doc.date.strftime('%Y-%m-%d'),
                                         status=doc.status,
                                         documentType=doc.type,
                                         xlsxUrl=doc.xlsx_image_url,
                                         xmlUrl=doc.xml_image_url,
                                         name=doc.file_name))

    return GetDocumentsResponse(declarations=list_documents_r)


@consumer(router=router, queue=document_queue, pattern="document.document-remove",
          request=RemoveDocumentRequest)
async def remove_document(request: RemoveDocumentRequest) -> RemoveDocumentResponse:
    """
    Роут на удаление документа. Также удаляет его из файловой системы контентного мс.
    :param request: объект на удаление документа RemoveDocumentRequest
    :return: response объект на удаление документа RemoveDocumentResponse
    """

    document = await Document.filter(id=request.id, user_id=request.userID).first()

    if not document:
        raise Exception("Документ не найден.")

    # Если есть ссылка удаляем файл на контентном мс
    if (document.xlsx_image_url is not None) or (document.xml_image_url is not None):
        try:
            if document.xlsx_image_url is not None:
                await ContentApi(user_id=request.userID).delete(file_url=document.xlsx_image_url)
            if document.xml_image_url is not None:
                await ContentApi(user_id=request.userID).delete(file_url=document.xml_image_url)

            # Удаляем документ из бд
            await document.delete()

        except IndexError:
            document.status = 'no_file'

    return RemoveDocumentResponse(id=request.id)
