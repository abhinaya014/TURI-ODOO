from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True, string="Player Name")
    email = fields.Char(required=True, string="Email", index=True, unique=True)
    password = fields.Char(required=True, string="Password")
    
    photo = fields.Image(string="Photo", max_width=512, max_height=512, attachment=True, store=False)
    
    level = fields.Integer(string="Level", default=1)
    experience = fields.Float(string="Experience", default=0)
    last_login = fields.Datetime(string="Last Login")
    registration_date = fields.Datetime(string="Registration Date", default=fields.Datetime.now)
    
    player_id = fields.Char(
        string="Player ID", copy=False, readonly=True, default=lambda self: self._generate_player_id()
    )
    
    active = fields.Boolean(default=True, string="Active")

    total_matches = fields.Integer(string="Total Matches", compute="_compute_totals", store=True)
    total_wins = fields.Integer(string="Total Wins", compute="_compute_totals", store=True)

    coin_transaction_ids = fields.One2many('game.coin.transaction', 'player_id', string="Coin Transactions", ondelete='cascade')
    coin_balance = fields.Float(string="Coin Balance", compute='_compute_coin_balance', store=True)

    owned_skins = fields.Many2many('game.skin', string="Owned Skins")
    match_stats_ids = fields.One2many('game.match.player.stats', 'player_id', string="Match Statistics")

    partner_id = fields.Many2one('res.partner', string="Contact", required=True, readonly=True, ondelete='cascade')
    win_rate = fields.Float(string="Win Rate", compute="_compute_win_rate", store=True)

    def _generate_player_id(self):
        """Genera un Player ID usando ir.sequence"""
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'game.player')], limit=1)
        return sequence.next_by_id() if sequence else False

    @api.depends('total_matches', 'total_wins')
    def _compute_win_rate(self):
        """Evita división por 0 y calcula el porcentaje de victorias"""
        for player in self:
            player.win_rate = (player.total_wins * 100 / player.total_matches) if player.total_matches > 0 else 0

    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.depends('match_stats_ids')
    def _compute_totals(self):
        for player in self:
            matches = self.env['game.match'].search([('player_stats_ids.player_id', '=', player.id)])
            player.total_matches = len(matches)
            player.total_wins = len(matches.filtered(lambda m: m.winner_id == player))

    @api.model
    def create(self, vals):
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()

        existing_partner = self.env['res.partner'].sudo().search([('email', '=', vals.get('email'))], limit=1)
        
        if not existing_partner:
            partner_vals = {
                'name': vals.get('name'),
                'email': vals.get('email')
            }
            if vals.get('photo'):
                partner_vals['image_1920'] = vals['photo']
            existing_partner = self.env['res.partner'].sudo().create(partner_vals)

        vals['partner_id'] = existing_partner.id
        player = super(GamePlayer, self).create(vals)

        if vals.get('photo'):
            existing_partner.sudo().write({'image_1920': vals['photo']})

        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 400,
            'reason': 'Initial registration bonus'
        })

        return player

    def write(self, vals):
        res = super(GamePlayer, self).write(vals)

        for player in self:
            partner_vals = {}
            if 'name' in vals:
                partner_vals['name'] = vals['name']
            if 'email' in vals:
                partner_vals['email'] = vals['email']
            if 'photo' in vals and vals['photo']:
                partner_vals['image_1920'] = vals['photo']
            
            if partner_vals:
                player.partner_id.sudo().write(partner_vals)

        return res
