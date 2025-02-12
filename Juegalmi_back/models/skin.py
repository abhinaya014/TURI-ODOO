from odoo import models, fields

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    photo = fields.Binary(string="Image")
    type = fields.Selection([
        ('character', 'Personaje'),  # Solo permitiremos "Character"
    ], string="Type", default='character', required=True)
    description = fields.Text()
    color = fields.Selection([
        ('red', 'Rojo'),
        ('blue', 'Azul'),
        ('green', 'Verde'),
        ('yellow', 'Amarillo'),
        ('pink', 'Rosa'),
        ('orange', 'Naranja')
    ], string="Color", required=True)

    owned_by_players = fields.Many2many(
        'game.player',
        string="Jugadores que tienen este skin"
    )
