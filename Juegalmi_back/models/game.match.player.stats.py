from odoo import models, fields, api

class GameMatchPlayerStats(models.Model):
    _name = 'game.match.player.stats'
    _description = 'Match Player Stats'

    player_id = fields.Many2one(
        'game.player', string="Player", required=True, ondelete="cascade"
    )
    match_id = fields.Many2one(
        'game.match', string="Match", required=True, ondelete="cascade"
    )

    match_date = fields.Datetime(
        string="Match Date", related="match_id.match_date", store=True
    )

    match_type = fields.Selection([
        ('ranked', 'Ranked'),
        ('casual', 'Casual'),
        ('tournament', 'Tournament')
    ], string="Match Type", required=True)

    kills = fields.Integer(string="Kills", default=0)
    deaths = fields.Integer(string="Deaths", default=0)
    score = fields.Integer(string="Score", default=0)

    result = fields.Selection([
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('draw', 'Draw')
    ], string="Result", required=True)

    # Computado para calcular la relación K/D Ratio
    kd_ratio = fields.Float(string="K/D Ratio", compute="_compute_kd_ratio", store=True)

    @api.depends('kills', 'deaths')
    def _compute_kd_ratio(self):
        """ Calcula el K/D Ratio, asegurando que no haya división por 0 """
        for record in self:
            if record.deaths == 0:
                record.kd_ratio = record.kills if record.kills > 0 else 0.0
            else:
                record.kd_ratio = record.kills / record.deaths

    @api.model
    def create(self, vals):
        """Verifica que no se cree una estadística duplicada para un mismo jugador en la misma partida"""
        existing_record = self.search([
            ('player_id', '=', vals.get('player_id')),
            ('match_id', '=', vals.get('match_id'))
        ], limit=1)

        if existing_record:
            raise ValueError("Este jugador ya tiene estadísticas registradas en esta partida.")

        return super(GameMatchPlayerStats, self).create(vals)

    def write(self, vals):
        """Evita que un resultado ya registrado sea cambiado manualmente"""
        if 'result' in vals:
            raise ValueError("No se puede modificar el resultado de una partida ya registrada.")
        return super(GameMatchPlayerStats, self).write(vals)
