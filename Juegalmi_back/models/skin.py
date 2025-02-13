from odoo import models, fields, api

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('character', 'Personaje'),
    ], string="Type", default='character', required=True)

    description = fields.Text()

    # Ahora este campo reemplaza la selección de colores y permite subir imágenes personalizadas
    image = fields.Image(string="Skin Image", help="Imagen personalizada del skin")

    owned_by_players = fields.Many2many(
        'game.player',
        string="Jugadores que poseen este skin"
    )

    # Contador automático de jugadores con este skin
    owned_by_players_count = fields.Integer(
        string="Número de jugadores",
        compute="_compute_owned_by_players_count",
        store=True
    )

    @api.depends('owned_by_players')
    def _compute_owned_by_players_count(self):
        """ Calcula el número de jugadores que poseen este skin """
        for skin in self:
            skin.owned_by_players_count = len(skin.owned_by_players)
