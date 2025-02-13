from odoo import models, fields

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('character', 'Personaje'),  # Solo permitiremos "Character"
    ], string="Type", default='character', required=True)
    description = fields.Text()

    # Nuevo: Imagen del skin en lugar de solo color
    image = fields.Image(string="Skin Image")  # Campo imagen

    # Si quieres seguir usando la lógica de colores, podrías almacenar la ruta en lugar de un campo Selection
    color_image = fields.Char(string="Color Image Path", help="Ruta de la imagen de color")  

    owned_by_players = fields.Many2many(
        'game.player',
        string="Jugadores que tienen este skin"
    )
