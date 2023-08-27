from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from tortoise.fields import ManyToManyField

class Room(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    messages = fields.ReverseRelation['Message']
    users = ManyToManyField('models.User', related_name='rooms')


    # an index on the name column
    class Meta:
        indexes = [
            ('name',)
        ]


    def __str__(self):
        return self.name

