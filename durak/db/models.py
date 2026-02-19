from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=255, null=True)

class Chat(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)

class Game(models.Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField("models.Chat", related_name="games")
    players = fields.ManyToManyField("models.User", related_name="games")
    status = fields.CharField(max_length=255)

class ChatSetting(models.Model):
    id = fields.IntField(pk=True)
    game_mode = fields.CharField(max_length=255, default="classic")
    card_theme = fields.CharField(max_length=255, default="classic")
    sticker_id_helper = fields.BooleanField(default=False)
