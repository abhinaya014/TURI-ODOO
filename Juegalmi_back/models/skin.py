from odoo import models, fields

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('weapon', 'Arma'),
        ('character', 'Personaje'),
    ], string="Tipo", default='weapon')
    description = fields.Text()
