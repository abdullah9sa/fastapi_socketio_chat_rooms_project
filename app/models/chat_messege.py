from tortoise import Model, fields

class Chat_Messege(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField('models.User', related_name='usrs')
    room = fields.ForeignKeyField('models.Room', related_name='rooms')

    # an index on the timestamp column for performance
    class Meta:
        indexes = [
            ('timestamp',)
        ]

    def __str__(self):
        return f'{self.user.username} in {self.room.name} at {self.timestamp}'
