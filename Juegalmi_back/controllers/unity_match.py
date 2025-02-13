from odoo import http
from odoo.http import request
import json

class GameAPIController(http.Controller):

    @http.route('/api/matches', type='json', auth='public', methods=['GET'])
    def get_all_matches(self):
        # Obtener todos los registros del modelo 'game.match'
        matches = request.env['game.match'].sudo().search([])

        # Formatear los datos
        match_list = []
        for match in matches:
            match_list.append({
                'match_id': match.name,
                'score': match.score,
                'start_time': match.start_time.strftime('%Y-%m-%d %H:%M:%S') if match.start_time else None,
                'end_time': match.end_time.strftime('%Y-%m-%d %H:%M:%S') if match.end_time else None,
                'duration': match.duration,
                'state': match.state,
                'winner': match.winner_id.name if match.winner_id else None,
                'notes': match.notes,
                'player_stats': [
                    {
                        'player_id': stat.player_id.id,
                        'player_name': stat.player_id.name,
                        'score': stat.score
                    }
                    for stat in match.player_stats_ids
                ]
            })

        return {'status': 'success', 'matches': match_list}

        @http.route('/game_api/achievements/check/<int:player_id>', type='http', auth='public', methods=['POST'], csrf=False)
        def check_achievements(self, player_id):
            try:
                player = request.env['game.player'].sudo().browse(player_id)
                if not player.exists():
                    return self._json_response({'status': 'error', 'message': 'Player not found'}, 404)

                achievements = request.env['game.achievement'].sudo().search([])
                new_achievements = []

                for achievement in achievements:
                    if achievement.check_achievement_for_player(player_id):
                        new_achievements.append({
                            'id': achievement.id,
                            'name': achievement.name,
                            'description': achievement.description,
                            'points': achievement.points,
                            'reward_coins': achievement.reward_coins
                        })

                return self._json_response({
                    'status': 'success',
                    'new_achievements': new_achievements
                })

            except Exception as e:
                _logger.error(f"Error checking achievements: {e}")
                return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)

