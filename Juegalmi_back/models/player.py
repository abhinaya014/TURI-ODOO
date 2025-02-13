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

    # 📌 Foto del jugador
    photo = fields.Image(string="Photo", max_width=512, max_height=512, attachment=True, store=False)

    level = fields.Integer(string="Level", default=1)
    experience = fields.Float(string="Experience", default=0)
    last_login = fields.Datetime(string="Last Login")
    registration_date = fields.Datetime(string="Registration Date", default=fields.Datetime.now)
    player_id = fields.Char(
        string="Player ID", 
        copy=False, 
        default=lambda self: self.env['ir.sequence'].next_by_code('game.player')
    )
    active = fields.Boolean(default=True, string="Active")

    total_matches = fields.Integer(string="Total Matches", compute="_compute_totals", store=True)
    total_wins = fields.Integer(string="Total Wins", compute="_compute_totals", store=True)
    win_rate = fields.Float(string="Win Rate", compute="_compute_win_rate", store=True)

    coin_transaction_ids = fields.One2many(
        'game.coin.transaction', 'player_id', string="Coin Transactions", ondelete='cascade'
    )
    coin_balance = fields.Float(string="Coin Balance", compute='_compute_coin_balance', store=True)

    owned_skins = fields.Many2many('game.skin', string="Owned Skins")
    match_stats_ids = fields.One2many('game.match.player.stats', 'player_id', string="Match Statistics")

    partner_id = fields.Many2one('res.partner', string="Contacto", required=True, readonly=True, ondelete='cascade')

    can_level_up = fields.Boolean(
        string="Can Level Up",
        compute="_compute_can_level_up",
        store=False
    )

    ### 📌 FUNCIONES COMPUTADAS ###
    
    @api.depends('coin_transaction_ids.amount')
    def _compute_coin_balance(self):
        """Calcula el saldo de monedas del jugador"""
        for player in self:
            player.coin_balance = sum(player.coin_transaction_ids.mapped('amount'))

    @api.depends('match_stats_ids')
    def _compute_totals(self):
        """Calcula el total de partidas jugadas y ganadas"""
        for player in self:
            matches = self.env['game.match'].search([('player_stats_ids.player_id', '=', player.id)])
            wins = len(matches.filtered(lambda m: m.winner_id == player))
            player.total_matches = len(matches)
            player.total_wins = wins

    @api.depends('total_matches', 'total_wins')
    def _compute_win_rate(self):
        """Calcula el porcentaje de victorias"""
        for player in self:
            if player.total_matches:
                player.win_rate = (player.total_wins / player.total_matches) * 100
            else:
                player.win_rate = 0.0

    @api.depends('experience', 'level')
    def _compute_can_level_up(self):
        """Determina si el jugador puede subir de nivel"""
        for player in self:
            player.can_level_up = player.experience >= (player.level * 100)

    ### 📌 ACCIONES ###

    def action_level_up(self):
        """Permite subir de nivel si se cumple con la experiencia necesaria"""
        for player in self:
            if player.experience < (player.level * 100):
                raise ValidationError("Necesitas más experiencia para subir de nivel.")
            
            player.level += 1
            player.experience -= (player.level * 100)
            _logger.info(f"Jugador {player.name} ha subido al nivel {player.level}")

    def action_view_matches(self):
        """Redirige a la vista de partidas jugadas por el jugador"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Matches',
            'res_model': 'game.match',
            'view_mode': 'tree,form',
            'domain': [('player_stats_ids.player_id', '=', self.id)],
            'context': {'default_player_id': self.id},
        }

    def action_view_achievements(self):
        """Redirige a la vista de logros del jugador"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Achievements',
            'res_model': 'game.achievement',
            'view_mode': 'tree,form',
            'domain': [('player_id', '=', self.id)],
            'context': {'default_player_id': self.id},
        }

    ### 📌 CREATE Y WRITE ###

    @api.model
    def create(self, vals):
        if 'registration_date' not in vals:
            vals['registration_date'] = fields.Datetime.now()

        # 🔹 Guardar la imagen también en res.partner
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

        # 🔹 Asegurar que la imagen se guarda en res.partner
        if 'photo' in vals and vals['photo']:
            partner.sudo().write({'image_1920': vals['photo']})

        # 🔹 Dar 400 monedas por defecto al nuevo jugador
        self.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': 400,
            'reason': 'Monedas iniciales por registro'
        })

        return player  # ✅ Asegúrate de que el return esté correctamente indentado

    def write(self, vals):
        """Sincroniza cambios en el jugador con res.partner"""
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
