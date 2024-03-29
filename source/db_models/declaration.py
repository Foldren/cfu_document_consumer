from enum import Enum
from tortoise import Model
from tortoise.fields import BigIntField, TextField, DateField, CharField, CharEnumField


class DeclarationStatus(str, Enum):
    process = "process"
    success = "success"
    error = "error"
    no_file = "no_file"


class Declaration(Model):
    id = BigIntField(pk=True)
    user_id = CharField(max_length=100, index=True)
    legal_entity_id = CharField(max_length=100, index=True, null=True)
    file_name = CharField(max_length=170, index=True)
    date = DateField(index=True)
    legal_entity_inn = TextField(maxlength=30, null=True)
    image_url = CharField(max_length=300, null=True)
    status = CharEnumField(enum_type=DeclarationStatus, description='Статус декларации',
                           default=DeclarationStatus.process)

    class Meta:
        table = "declarations"
