from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GameResource(models.Model):
    _name = 'game.resource'
    _description = 'Game Resource'
    _order = 'name'

    name = fields.Char(string='Resource Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    category = fields.Selection([
        ('weapon', 'Weapon'),
        ('skin', 'Skin'),
        ('ability', 'Ability'),
    ], string='Category', required=True)
    availability = fields.Boolean(string='Available', default=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=lambda self: self.env.company.currency_id.id)
    image = fields.Binary(string='Image', attachment=True)

    def toggle_availability(self):
        for record in self:
            record.availability = not record.availability


class PlayerInventory(models.Model):
    _name = 'player.inventory'
    _description = 'Player Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    player_id = fields.Many2one('game.player', string='Player', required=True, tracking=True, ondelete='cascade')
    resource_id = fields.Many2one('game.resource', string='Resource', required=True, tracking=True, ondelete='restrict')
    acquisition_date = fields.Datetime(string='Acquisition Date', default=fields.Datetime.now, tracking=True)
    quantity = fields.Integer(string='Quantity', default=1, tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active', tracking=True)

    _sql_constraints = [
        ('unique_player_resource', 'unique(player_id, resource_id)', 
         'Player already has this resource!')
    ]


class GamePlayer(models.Model):
    _name = 'game.player'
    _description = 'Game Player'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'level desc, name'

    name = fields.Char(string='Username', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    password = fields.Char(string='Password', required=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    level = fields.Integer(string='Level', default=1, tracking=True)
    experience = fields.Integer(string='Experience Points', default=0, tracking=True)
    last_login = fields.Datetime(string='Last Login', tracking=True)
    registration_date = fields.Date(string='Registration Date', default=fields.Date.today, tracking=True)
    inventory_ids = fields.One2many('player.inventory', 'player_id', string='Inventory')
    match_ids = fields.Many2many('game.match', 'player_match_rel', 'player_id', 'match_id', 
                                string='Matches', tracking=True)
    image = fields.Binary(string='Avatar', attachment=True)
    total_matches = fields.Integer(string='Total Matches', compute='_compute_match_stats', store=True)
    wins = fields.Integer(string='Wins', compute='_compute_match_stats', store=True)
    win_rate = fields.Float(string='Win Rate (%)', compute='_compute_match_stats', store=True)
    
    _sql_constraints = [
        ('unique_username', 'unique(name)', 'Username must be unique!'),
        ('unique_email', 'unique(email)', 'Email must be unique!')
    ]

    @api.depends('match_ids', 'match_ids.state', 'match_ids.winner_id')
    def _compute_match_stats(self):
        for player in self:
            finished_matches = player.match_ids.filtered(lambda m: m.state == 'finished')
            player.total_matches = len(finished_matches)
            player.wins = len(finished_matches.filtered(lambda m: m.winner_id == player))
            player.win_rate = (player.wins / player.total_matches * 100) if player.total_matches > 0 else 0

    @api.constrains('level')
    def _check_level(self):
        for player in self:
            if player.level < 1:
                raise ValidationError('Level cannot be less than 1!')

    def add_experience(self, amount):
        self.ensure_one()
        self.experience += amount
        # Lógica simple de subida de nivel (cada 1000 puntos)
        while self.experience >= 1000:
            self.level += 1
            self.experience -= 1000


class GameMatch(models.Model):
    _name = 'game.match'
    _description = 'Game Match'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_time desc'

    name = fields.Char(string='Match ID', required=True, copy=False, 
                      default=lambda self: self.env['ir.sequence'].next_by_code('game.match'))
    start_time = fields.Datetime(string='Start Time', tracking=True)
    end_time = fields.Datetime(string='End Time', tracking=True)
    duration = fields.Float(string='Duration (minutes)', compute='_compute_duration', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    player_ids = fields.Many2many('game.player', 'player_match_rel', 'match_id', 'player_id', 
                                 string='Players', tracking=True)
    winner_id = fields.Many2one('game.player', string='Winner', tracking=True)
    match_type = fields.Selection([
        ('duel', '1v1'),
        ('team', 'Team Match'),
        ('battle_royale', 'Battle Royale')
    ], string='Match Type', required=True, default='duel')
    score = fields.Integer(string='Score', tracking=True)
    notes = fields.Text(string='Match Notes', tracking=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for match in self:
            if match.start_time and match.end_time:
                duration = (match.end_time - match.start_time).total_seconds() / 60
                match.duration = round(duration, 2)
            else:
                match.duration = 0

    @api.constrains('player_ids')
    def _check_players_count(self):
        for match in self:
            if match.match_type == 'duel' and len(match.player_ids) != 2:
                raise ValidationError('Duel matches must have exactly 2 players!')
            elif match.match_type == 'team' and len(match.player_ids) != 4:
                raise ValidationError('Team matches must have exactly 4 players!')
            elif match.match_type == 'battle_royale' and len(match.player_ids) < 10:
                raise ValidationError('Battle Royale matches must have at least 10 players!')

    def action_start_match(self):
        self.ensure_one()
        if not self.player_ids:
            raise ValidationError('Cannot start match without players!')
        self.write({
            'state': 'in_progress',
            'start_time': fields.Datetime.now()
        })

    def action_end_match(self):
        self.ensure_one()
        if not self.winner_id:
            raise ValidationError('Cannot end match without declaring a winner!')
        self.write({
            'state': 'finished',
            'end_time': fields.Datetime.now()
        })
        # Dar experiencia al ganador
        self.winner_id.add_experience(100)
        # Dar experiencia a los participantes
        for player in self.player_ids - self.winner_id:
            player.add_experience(50)

    def action_cancel_match(self):
        if self.state == 'finished':
            raise ValidationError('Cannot cancel a finished match!')
        self.write({'state': 'cancelled'})