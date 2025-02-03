from odoo import models, fields

class GameCoinTransaction(models.Model):
    _name = 'game.coin.transaction'
    _description = 'Transacción de Monedas'

    player_id = fields.Many2one('game.player', string="Jugador", required=True)
    amount = fields.Float(string="Monto", required=True,
                          help="Monto positivo para agregar monedas, negativo para quitar.")
    reason = fields.Char(string="Razón", help="Motivo de la transacción")
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now)
