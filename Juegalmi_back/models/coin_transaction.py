from odoo import models, fields

class GameCoinTransaction(models.Model):
    _name = 'game.coin.transaction'
    _description = 'Coin Transaction for a Player'

    player_id = fields.Many2one('game.player', string="Jugador", required=True)
    amount = fields.Float(string="Amount", required=True,
                          help="Positive to add coins, negative to subtract coins")
    reason = fields.Char(string="Reason", help="Reason for the transaction")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
