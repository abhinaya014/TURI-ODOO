from odoo import models, fields

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    photo = fields.Binary(string="Image")
    type = fields.Selection([
        ('weapon', 'Arma'),
        ('character', 'Personaje'),
        # Puedes agregar más tipos según sea necesario
    ], string="Type", default='weapon')
    description = fields.Text()
