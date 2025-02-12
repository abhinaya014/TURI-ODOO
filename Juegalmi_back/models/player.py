from odoo import models, fields, api

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    password = fields.Char(required=True)
    photo = fields.Binary(string="Photo", attachment=True)
    level = fields.Integer(string="Level", default=1)
    experience = fields.Float(string="Experience", default=0)
    last_login = fields.Datetime(string="Last Login")
    registration_date = fields.Datetime(string="Registration Date", default=fields.Datetime.now)
    player_id = fields.Char(string="Player ID", copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('game.player'))
    active = fields.Boolean(default=True, string="Active")

    total_matches = fields.Integer(string="Total Matches", compute="_compute_totals", store=True)
    total_wins = fields.Integer(string="Total Wins", compute="_compute_totals", store=True)
    coin_transaction_ids = fields.One2many('game.coin.transaction', 'player_id', string="Coin Transactions")
    coin_balance = fields.Float(string="Coin Balance", compute='_compute_coin_balance', store=True)
    match_ids = fields.Many2many('game.match', string="Matches Played", compute="_compute_matches_played", store=False)
    partner_id = fields.Many2one('res.partner', string="Contacto", readonly=True)

    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.depends('match_ids.state', 'match_ids.winner_id')
    def _compute_totals(self):
        for player in self:
            matches = self.env['game.match'].search([('player_ids', 'in', player.id)])
            wins = len(matches.filtered(lambda m: m.winner_id == player))
            player.total_matches = len(matches)
            player.total_wins = wins

    @api.depends('match_ids')
    def _compute_matches_played(self):
        for player in self:
            matches = self.env['game.match'].search([('player_ids', 'in', player.id)])
            player.match_ids = matches

    @api.model
    def create(self, vals):
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()

        player = super(GamePlayer, self).create(vals)

        # Transacción inicial de monedas
        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 200,
            'reason': 'Default initial coins',
        })

        # Crear el contacto en res.partner
        partner_vals = {z
            'name': player.name,
            'email': player.email,
        }
        if vals.get('photo'):
            partner_vals['image_1920'] = vals['photo']

        partner = self.env['res.partner'].create(partner_vals)
        player.partner_id = partner.id
        return player
