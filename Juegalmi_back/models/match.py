from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GameMatch(models.Model):
    _name = 'game.match'
    _description = 'Game Match'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_time desc'

    name = fields.Char(
        string='Match ID', 
        required=True, 
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('game.match')
    )
    score = fields.Float(string='Total Match Score', default=0.0)
    start_time = fields.Datetime(string='Start Time', tracking=True)
    end_time = fields.Datetime(string='End Time', tracking=True)
    duration = fields.Float(string='Duration (minutes)', compute='_compute_duration', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    player_stats_ids = fields.One2many(
        'game.match.player.stats', 
        'match_id', 
        string='Player Statistics', 
        tracking=True
    )

    winner_id = fields.Many2one('game.player', string='Winner', tracking=True)

    notes = fields.Text(string='Match Notes', tracking=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for match in self:
            if match.start_time and match.end_time:
                duration = (match.end_time - match.start_time).total_seconds() / 60
                match.duration = round(duration, 2)
            else:
                match.duration = 0

    @api.constrains('player_stats_ids')
    def _check_players_count(self):
        for match in self:
            player_count = len(match.player_stats_ids)
            if player_count < 2 or player_count > 8:
                raise ValidationError('Matches must have between 2 and 8 players.')

    @api.model
    def start_match(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError('Only matches in draft state can be started.')
        self.write({'state': 'in_progress', 'start_time': fields.Datetime.now()})

    def end_match(self, winner_id, total_score):
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError('Only matches in progress can be finished.')
        self.write({
            'state': 'finished',
            'end_time': fields.Datetime.now(),
            'winner_id': winner_id,
            'score': total_score
        })

    def cancel_match(self):
        self.ensure_one()
        if self.state not in ['draft', 'in_progress']:
            raise ValidationError('Only draft or in-progress matches can be cancelled.')
        self.write({'state': 'cancelled'})
