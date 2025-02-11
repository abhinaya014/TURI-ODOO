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

