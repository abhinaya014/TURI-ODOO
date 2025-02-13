from odoo import models, fields, api  # Asegúrate de importar api

class GameSkin(models.Model):
    _name = 'game.skin'
    _description = 'Game Skin'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('character', 'Personaje'),
    ], string="Type", default='character', required=True)
    description = fields.Text()
    image_url = fields.Char(string="Image URL")
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

    @api.model
    def create(self, vals):
        if vals.get('image_url'):
            # Convertir la ruta relativa a una URL completa
            image_url = vals['image_url']
            if image_url.startswith('/'):
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                vals['image_url'] = f"{base_url}{image_url}"
        return super(GameSkin, self).create(vals)