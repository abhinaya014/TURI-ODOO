from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)

class GameAchievement(models.Model):
    _name = 'game.achievement'
    _description = 'Game Achievement'
    _order = 'sequence'

    name = fields.Char(required=True)
    description = fields.Text()
    points = fields.Integer(default=100)
    sequence = fields.Integer(default=10)
    icon = fields.Binary(string="Achievement Icon")
    achievement_type = fields.Selection([
        ('kills', '🎯 Kill Master'),
        ('matches', '🎮 Match Master'),
        ('coins', '💰 Coin Collector'),
        ('wins', '🏆 Victory Master'),
        ('skins', '🎨 Skin Collector')
    ], required=True)
    threshold = fields.Integer(string="Achievement Threshold", required=True)
    rarity = fields.Selection([
        ('common', '🟢 Common'),
        ('rare', '🟡 Rare'),
        ('epic', '🟣 Epic'),
        ('legendary', '🔴 Legendary')
    ], required=True, default='common')
    reward_coins = fields.Integer(string="Coin Reward", default=0)
    player_ids = fields.Many2many('game.player', string="Players who achieved")
    active = fields.Boolean(default=True)

    def check_achievement_for_player(self, player_id):
        player = self.env['game.player'].browse(player_id)
        if not player.exists() or player.id in self.player_ids.ids:
            return False

        achieved = False
        if self.achievement_type == 'kills':
            total_kills = sum(player.match_stats_ids.mapped('kills'))
            achieved = total_kills >= self.threshold
        elif self.achievement_type == 'matches':
            achieved = player.total_matches >= self.threshold
        elif self.achievement_type == 'wins':
            achieved = player.total_wins >= self.threshold
        elif self.achievement_type == 'coins':
            achieved = player.coin_balance >= self.threshold
        elif self.achievement_type == 'skins':
            achieved = len(player.owned_skins) >= self.threshold

        if achieved:
            self.player_ids = [(4, player.id)]
            if self.reward_coins > 0:
                self.env['game.coin.transaction'].create({
                    'player_id': player.id,
                    'amount': self.reward_coins,
                    'reason': f'Achievement Reward: {self.name}'
                })
            return True
        return False