from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
