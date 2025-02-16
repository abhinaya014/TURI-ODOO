from odoo import models, fields, api

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

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW game_statistics AS
            SELECT 
                p.id as id,
                p.name as name,
                COUNT(DISTINCT p.id) as total_players,
                COUNT(DISTINCT m.id) as total_matches,
                p.total_wins as victories,
                p.coin_balance as total_coins,
                COUNT(DISTINCT s.id) as skins_owned
            FROM game_player p
            LEFT JOIN game_match m ON m.winner_id = p.id
            LEFT JOIN game_player_game_skin_rel ps ON ps.game_player_id = p.id
            LEFT JOIN game_skin s ON s.id = ps.game_skin_id
            GROUP BY p.id, p.name, p.total_wins, p.coin_balance
        """)