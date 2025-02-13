from odoo import models, fields, api

class GameCoinTransaction(models.Model):
    _name = 'game.coin.transaction'
    _description = 'Coin Transaction for a Player'
    _order = 'date desc'

    player_id = fields.Many2one(
        'game.player', 
        string="Jugador", 
        required=True, 
        ondelete='cascade'
    )

    amount = fields.Float(
        string="Amount", 
        required=True,
        help="Positive to add coins, negative to subtract coins"
    )

    reason = fields.Char(
        string="Reason", 
        help="Reason for the transaction"
    )

    date = fields.Datetime(
        string="Date", 
        default=fields.Datetime.now
    )

    player_balance = fields.Float(
        string="Balance Actual",
        compute='_compute_player_balance',
        store=False
    )

    @api.depends('player_id')
    def _compute_player_balance(self):
        for record in self:
            if record.player_id:
                record.player_balance = record.player_id.coin_balance
            else:
                record.player_balance = 0.0