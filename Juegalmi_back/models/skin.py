from odoo import models, fields, api

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('character', 'Personaje'),
    ], string="Type", default='character', required=True)
    description = fields.Text()
    image_url = fields.Selection([
        ('Juegalmi_back\static\img\skin_red.png', 'Red Skin'),
        ('/juegalmi_back\static\img\skin_blue.png', 'Blue Skin'),
        ('/juegalmi_back\static\img\skin_green.png', 'Green Skin'),
        ('/juegalmi_back\static\img\skin_yellow.png', 'Yellow Skin'),
        ('/juegalmi_back\static\img\skin_pink.png', 'Pink Skin'),
        ('/juegalmi_back\static\img\skin_orange.png', 'Orange Skin'),
    ], string="Skin Image", required=True)
    owned_by_players = fields.Many2many(
        'game.player',
        string="Jugadores que tienen este skin"
    )
    player_count = fields.Integer(
        string="Cantidad de Jugadores",
        compute='_compute_player_count'
    )

    def _compute_player_count(self):
        for skin in self:
            skin.player_count = len(skin.owned_by_players)