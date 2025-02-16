from odoo import models, fields, api
from odoo import tools

class GameStatistics(models.Model):
    _name = 'game.statistics'
    _description = 'Game Statistics Dashboard'
    _auto = False

    name = fields.Char(string='Nombre')
    total_players = fields.Integer(string='Total Jugadores')
    total_matches = fields.Integer(string='Total Partidas')
    victories = fields.Integer(string='Victorias')
    total_coins = fields.Float(string='Total Monedas')
    skins_owned = fields.Integer(string='Skins Comprados')
    level = fields.Integer(string='Nivel')
    experience = fields.Float(string='Experiencia')
    total_kills = fields.Integer(string='Kills Totales')
    total_deaths = fields.Integer(string='Muertes Totales')
    kd_ratio = fields.Float(string='Ratio K/D', compute='_compute_kd_ratio')

    @api.depends('total_kills', 'total_deaths')
    def _compute_kd_ratio(self):
        for record in self:
            record.kd_ratio = record.total_kills / record.total_deaths if record.total_deaths > 0 else 0.0

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW game_statistics AS (
                SELECT 
                    p.id as id,
                    p.name as name,
                    COUNT(DISTINCT player.id) as total_players,
                    COUNT(DISTINCT m.id) as total_matches,
                    p.total_wins as victories,
                    p.coin_balance as total_coins,
                    COUNT(DISTINCT s.id) as skins_owned,
                    p.level as level,
                    p.experience as experience,
                    COALESCE(SUM(ms.kills), 0) as total_kills,
                    COALESCE(SUM(ms.deaths), 0) as total_deaths
                FROM game_player p
                CROSS JOIN game_player player
                LEFT JOIN game_match m ON m.winner_id = p.id
                LEFT JOIN game_player_game_skin_rel ps ON ps.game_player_id = p.id
                LEFT JOIN game_skin s ON s.id = ps.game_skin_id
                LEFT JOIN game_match_player_stats ms ON ms.player_id = p.id
                GROUP BY p.id, p.name, p.total_wins, p.coin_balance, p.level, p.experience
            )
        """)