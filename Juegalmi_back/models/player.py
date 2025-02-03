from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    password = fields.Char(required=True)
    photo = fields.Binary(string="Photo")
    level = fields.Integer(string="Level", default=1)
    experience = fields.Float(string="Experience", default=0)
    last_login = fields.Datetime(string="Last Login")
    registration_date = fields.Datetime(string="Registration Date", default=fields.Datetime.now)
    player_id = fields.Char(string="Player ID", copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('game.player'))
    active = fields.Boolean(default=True, string="Active")

    # Totales (se pueden calcular a partir de los partidos)
    total_matches = fields.Integer(string="Total Matches", compute="_compute_totals", store=True)
    total_wins = fields.Integer(string="Total Wins", compute="_compute_totals", store=True)

    # Relación con transacciones de monedas
    coin_transaction_ids = fields.One2many('game.coin.transaction', 'player_id', string="Coin Transactions")
    coin_balance = fields.Float(string="Coin Balance", compute='_compute_coin_balance', store=True)

    # (Opcional) Para listar los partidos jugados, se puede hacer un campo computed (buscando en game.match)
    match_ids = fields.Many2many('game.match', string="Matches Played", compute="_compute_matches_played", store=False)

    partner_id = fields.Many2one('res.partner', string="Contacto", readonly=True)

    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.depends()
    def _compute_matches_played(self):
        # Busca en game.match aquellos registros donde el jugador aparezca en player_ids.
        for player in self:
            matches = self.env['game.match'].search([('player_ids', 'in', player.id)])
            player.match_ids = matches

    @api.depends('match_ids', 'match_ids.state', 'match_ids.winner_id')
    def _compute_totals(self):
        for player in self:
            matches = self.env['game.match'].search([('player_ids', 'in', player.id)])
            wins = self.env['game.match'].search_count([('winner_id', '=', player.id)])
            player.total_matches = len(matches)
            player.total_wins = wins

    def add_experience(self, points):
        for rec in self:
            rec.experience += points
            # Opcional: puedes definir reglas para aumentar el nivel según la experiencia acumulada.
    
    @api.model
    def create(self, vals):
        # Asigna la fecha de registro si no se indica
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()
        # Crea el registro del jugador
        player = super(GamePlayer, self).create(vals)
        # Asigna 200 monedas por defecto (crea una transacción inicial)
        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 200,
            'reason': 'Default initial coins',
        })
        # Crea el contacto en res.partner para integrarlo en el módulo de Contactos
        partner_vals = {
            'name': player.name,
            'email': player.email,
        }
        partner = self.env['res.partner'].create(partner_vals)
        player.partner_id = partner.id
        return player
