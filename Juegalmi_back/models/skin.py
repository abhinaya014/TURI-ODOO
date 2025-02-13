from odoo import models, fields

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    image = fields.Char(string="Skin Image", required=True, help="Ruta de la imagen dentro del módulo, por ejemplo: /your_module_name/static/img/skin_red.png")

    owned_by_players = fields.Many2many(
        'game.player',
        string="Jugadores que tienen este skin"
    )
