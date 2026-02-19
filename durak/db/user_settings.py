from tortoise import fields, models

class UserSetting(models.Model):
    id = fields.IntField(pk=True)
    stats = fields.BooleanField(default=True)
    first_places = fields.IntField(default=0)
    games_played = fields.IntField(default=0)
    cards_atack = fields.IntField(default=0)
    cards_beaten = fields.IntField(default=0)
