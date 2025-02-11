from odoo import http
from odoo.http import request
import json

class GameAPIController(http.Controller):    

    @http.route('/api/match/stats', type='json', auth='public', methods=['POST'])
    def record_match_stats(self, **kwargs):
        data = json.loads(request.httprequest.data)
        
        match_id = data.get('match_id')
        stats = data.get('player_stats', [])

        match = request.env['game.match'].browse(match_id)
        if not match:
            return {'status': 'error', 'message': 'Match not found.'}

        return {'status': 'success', 'message': 'Player stats recorded successfully'}
