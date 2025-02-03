from odoo import models, fields, api

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    password = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', string="Contacto", readonly=True)
    
    # Relación con transacciones de monedas
    coin_transaction_ids = fields.One2many('game.coin.transaction', 'player_id', string="Transacciones")
    coin_balance = fields.Float(compute='_compute_coin_balance', store=True)

    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.model
    def create(self, vals):
        partner_vals = {
            'name': vals.get('name'),
            'email': vals.get('email'),
        }
        partner = self.env['res.partner'].create(partner_vals)
        vals['partner_id'] = partner.id
        return super(GamePlayer, self).create(vals)
