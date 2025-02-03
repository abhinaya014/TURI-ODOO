from odoo import models, fields, api

class GameMatch(models.Model):
    _name = 'game.match'
    _description = 'Partido de Juego'

    name = fields.Char(string='Nombre del Partido')
    start_date = fields.Datetime(string='Fecha Inicio')
    end_date = fields.Datetime(string='Fecha Fin')
    winner_id = fields.Many2one('game.player', string="Ganador")
    score = fields.Char(string="Score")
    player_ids = fields.Many2many('game.player', string="Jugadores")

    @api.constrains('player_ids')
    def _check_player_count(self):
        for match in self:
            count = len(match.player_ids)
            if count < 2 or count > 16:
                raise models.ValidationError("El partido debe tener entre 2 y 16 jugadores.")
