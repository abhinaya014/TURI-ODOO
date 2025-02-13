from odoo import models, fields, api
from odoo.exceptions import ValidationError
import bcrypt
import logging

_logger = logging.getLogger(__name__)

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True)
    email = fields.Char(required=True, unique=True)
    password_hash = fields.Char(string="Password Hash", readonly=True)

    # 🔹 Usamos Image para la foto
    photo = fields.Image(string="Photo", max_width=512, max_height=512, attachment=True, store=False)

    level = fields.Integer(string="Level", default=1)
    experience = fields.Float(string="Experience", default=0)
    last_login = fields.Datetime(string="Last Login")
    registration_date = fields.Datetime(string="Registration Date", default=fields.Datetime.now)
    player_id = fields.Char(string="Player ID", copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('game.player'))
    active = fields.Boolean(default=True, string="Active")

    total_matches = fields.Integer(string="Total Matches", compute="_compute_totals", store=True)
    total_wins = fields.Integer(string="Total Wins", compute="_compute_totals", store=True)

    coin_transaction_ids = fields.One2many('game.coin.transaction', 'player_id', string="Coin Transactions", ondelete='cascade')
    coin_balance = fields.Float(string="Coin Balance", compute='_compute_coin_balance', store=True)

    owned_skins = fields.Many2many('game.skin', string="Owned Skins")
    match_stats_ids = fields.One2many('game.match.player.stats', 'player_id', string="Match Statistics")

    partner_id = fields.Many2one('res.partner', string="Contacto", required=True, readonly=True, ondelete='cascade')

    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.depends('match_stats_ids')
    def _compute_totals(self):
        for player in self:
            matches = self.env['game.match'].search([('player_stats_ids.player_id', '=', player.id)])
            wins = len(matches.filtered(lambda m: m.winner_id == player))
            player.total_matches = len(matches)
            player.total_wins = wins

    @api.model
    def create(self, vals):
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()

        # 🔹 Hashear la contraseña antes de guardar
        if 'password' in vals:
            vals['password_hash'] = bcrypt.hashpw(vals['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            del vals['password']

        # 🔹 Guardar la imagen en res.partner
        partner = self.env['res.partner'].sudo().search([('email', '=', vals.get('email'))], limit=1)
        if not partner:
            partner_vals = {
                'name': vals.get('name'),
                'email': vals.get('email'),
            }
            if vals.get('photo'):
                partner_vals['image_1920'] = vals['photo']
            partner = self.env['res.partner'].sudo().create(partner_vals)

        vals['partner_id'] = partner.id
        player = super(GamePlayer, self).create(vals)

        # 🔹 Guardar imagen en res.partner
        if 'photo' in vals and vals['photo']:
            partner.sudo().write({'image_1920': vals['photo']})

        # 🔹 Dar 400 monedas por defecto al nuevo jugador
        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 400,
            'reason': 'Monedas iniciales por registro'
        })

        return player

    def write(self, vals):
        """Sincroniza cambios en el jugador con res.partner"""
        if 'password' in vals:
            vals['password_hash'] = bcrypt.hashpw(vals['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            del vals['password']

        res = super(GamePlayer, self).write(vals)

        for player in self:
            if 'name' in vals or 'email' in vals or 'photo' in vals:
                partner_vals = {}
                if 'name' in vals:
                    partner_vals['name'] = vals['name']
                if 'email' in vals:
                    partner_vals['email'] = vals['email']
                if 'photo' in vals:
                    partner_vals['image_1920'] = vals['photo']
                player.partner_id.sudo().write(partner_vals)

        return res

    def verify_password(self, password):
        """Verifica si la contraseña ingresada coincide con la almacenada"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
