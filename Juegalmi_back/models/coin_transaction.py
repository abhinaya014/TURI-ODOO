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


    def award_achievement(self, player_id):
    player = self.env['game.player'].browse(player_id)
    if player.exists() and player.id not in self.player_ids.ids:
        # Crear la transacción de monedas
        if self.reward_coins > 0:
            self.env['game.coin.transaction'].create({
                'player_id': player.id,
                'amount': self.reward_coins,
                'reason': f'Logro desbloqueado: {self.name}',
                'date': fields.Datetime.now()
            })
        # Añadir el jugador a la lista de jugadores que han conseguido el logro
        self.write({
            'player_ids': [(4, player.id, 0)]
        })
        return True
    return False