from odoo import http
from odoo.http import request
import json

class GameAPIController(http.Controller):

@http.route('/api/match/stats', type='json', auth='user', methods=['POST'])
    def record_match_stats(self, **kwargs):
        data = json.loads(request.httprequest.data)
        
        match_id = data.get('match_id')
        stats = data.get('player_stats', [])

        match = request.env['game.match'].sudo().browse(match_id)
        if not match:
            return {'status': 'error', 'message': 'Match not found.'}

        # Limpiar estadísticas anteriores si es necesario
        match.player_stats_ids.unlink()

        # Crear nuevas estadísticas
        for player_stat in stats:
            request.env['game.match.player.stats'].create({
                'match_id': match_id,
                'player_id': player_stat['player_id'],
                'kills': player_stat['kills'],
                'deaths': player_stat['deaths'],
                'score': player_stat['score'],
            })

        return {'status': 'success', 'message': 'Player stats recorded successfully'}
