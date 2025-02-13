from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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

    def action_view_stats(self):
    return {
        'name': 'Estadísticas del Jugador',
        'type': 'ir.actions.act_window',
        'res_model': 'game.match.player.stats',
        'view_mode': 'tree,form',
        'domain': [('player_id', '=', self.id)],
    }

    @api.model
    def create(self, vals):
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()

        # Verificar si el contacto ya existe en res.partner
        partner = self.env['res.partner'].sudo().search([('email', '=', vals.get('email'))], limit=1)

        if not partner:
            partner_vals = {
                'name': vals.get('name'),
                'email': vals.get('email'),
            }
            if vals.get('photo'):
                partner_vals['image_1920'] = vals['photo']
            partner = self.env['res.partner'].sudo().create(partner_vals)

        vals['partner_id'] = partner.id  # Asignamos el partner_id antes de crear el jugador
        player = super(GamePlayer, self).create(vals)

        try:
            # Obtener la compañía por defecto
            company = self.env['res.company'].sudo().search([], limit=1)
            if not company:
                raise ValidationError("No se encontró una compañía en Odoo. Configura una antes de continuar.")

            # Verificar si el grupo 'base.group_user' existe
            user_group = self.env.ref('base.group_user', raise_if_not_found=False)
            if not user_group:
                raise ValidationError("El grupo 'base.group_user' no está disponible en Odoo.")

            # Verificar si ya existe un usuario con el mismo email
            existing_user = self.env['res.users'].sudo().search([('login', '=', player.email)], limit=1)
            if not existing_user:
                user_vals = {
                    'name': player.name,
                    'login': player.email,
                    'partner_id': partner.id,
                    'password': vals.get('password'),
                    'groups_id': [(6, 0, [user_group.id])],  # Grupo de usuarios normales
                    'company_id': company.id,  # Asignar compañía por defecto
                    'company_ids': [(6, 0, [company.id])],  # Asegurar que tenga acceso a la compañía
                }
                self.env['res.users'].sudo().create(user_vals)

        except Exception as e:
            _logger.error(f"Error al crear usuario en res.users: {e}")

        return player

    def write(self, vals):
        """Sincroniza cambios en el jugador con res.partner"""
        res = super(GamePlayer, self).write(vals)

        for player in self:
            if 'name' in vals or 'email' in vals:
                partner_vals = {}
                if 'name' in vals:
                    partner_vals['name'] = vals['name']
                if 'email' in vals:
                    partner_vals['email'] = vals['email']
                player.partner_id.sudo().write(partner_vals)

        return res
