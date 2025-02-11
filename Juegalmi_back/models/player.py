from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    password = fields.Char(string="Password")  # Este campo es solo para entrada temporal
    photo = fields.Binary(string="Photo", attachment=True)
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

    # Relación One2many con estadísticas de partidas
    match_stats_ids = fields.One2many('game.match.player.stats', 'player_id', string="Match Statistics")

    partner_id = fields.Many2one('res.partner', string="Contacto", readonly=True)
    user_id = fields.Many2one('res.users', string="User", readonly=True)

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

        # **Crear usuario en res.users (el único lugar donde usamos password)**
        user_vals = {
            'name': vals.get('name'),
            'login': vals.get('email'),
            'password': vals.get('password')  # Correcto: solo aquí usamos la contraseña
        }
        user = self.env['res.users'].sudo().create(user_vals)

        # **Crear el jugador**
        vals['user_id'] = user.id
        player = super(GamePlayer, self).create(vals)

        # **Crear el contacto en res.partner (sin pasar la contraseña)**
        partner_vals = {
            'name': player.name,
            'email': player.email,
        }
        if vals.get('photo'):
            partner_vals['image_1920'] = vals['photo']

        # **Asegúrate de que partner no recibe campos no esperados**
        partner = self.env['res.partner'].create(partner_vals)
        player.partner_id = partner.id

        # **Transacción inicial de monedas**
        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 200,
            'reason': 'Default initial coins',
        })
        return player

    def write(self, vals):
        # ** Si se actualiza la contraseña, asegúrate de hacerlo en res.users **
        if 'password' in vals and self.user_id:
            self.user_id.sudo().write({'password': vals['password']})

        return super(GamePlayer, self).write(vals)
