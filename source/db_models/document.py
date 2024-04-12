from enum import Enum
from tortoise import Model
from tortoise.fields import BigIntField, TextField, DateField, CharField, CharEnumField


class DocumentStatus(str, Enum):
    process = "process"
    success = "success"
    error = "error"
    no_file = "no_file"


class DocumentType(str, Enum):
    declaration = 'declaration'
    advance_payment = 'advance_payment'


class Document(Model):
    id = BigIntField(pk=True)
    user_id = CharField(max_length=100, index=True)
    legal_entity_id = CharField(max_length=100, index=True, null=True)
    date = DateField(index=True)
    legal_entity_inn = TextField(maxlength=30, null=True)
    xlsx_image_url = CharField(max_length=300, null=True)
    xml_image_url = CharField(max_length=300, null=True)
    type = CharEnumField(enum_type=DocumentType, description='Тип документа',
                         default=DocumentType.declaration)
    status = CharEnumField(enum_type=DocumentStatus, description='Статус документа',
                           default=DocumentStatus.process)

    class Meta:
        table = "documents"
