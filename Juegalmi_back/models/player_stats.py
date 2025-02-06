from odoo import models, fields

class GameMatchPlayerStats(models.Model):
    _name = 'game.match.player.stats'
    _description = 'Player Stats in a Game Match'

    match_id = fields.Many2one('game.match', string='Match', ondelete='cascade')
    player_id = fields.Many2one('game.player', string='Player', required=True, ondelete='cascade')
    kills = fields.Integer(string='Kills', default=0)
    deaths = fields.Integer(string='Deaths', default=0)
    score = fields.Float(string='Score', default=0)
