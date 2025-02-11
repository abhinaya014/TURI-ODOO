from odoo import http
from odoo.http import request
import json

class UnityMatchController(http.Controller):

    @http.route('/api/match', type='json', auth='public', methods=['POST'])
    def create_match(self):
        try:
            # Obtener los datos JSON de la solicitud manualmente
            data = request.httprequest.get_json()

            # Asegúrate de que los datos estén bien recibidos
            name = data.get('name')
            players = data.get('players')

            if not name or not players or len(players) < 2:
                return {'error': 'El nombre del partido y al menos 2 jugadores son obligatorios.'}

            # Crear el match
            match = request.env['game.match'].create({
                'name': name,
                'start_time': data.get('start_time'),
                'end_time': data.get('end_time'),
                'winner_id': data.get('winner_id'),
                'score': data.get('total_score'),
                'state': 'draft',
            })

            # Crear estadísticas de jugadores
            for player in players:
                request.env['game.match.player.stats'].create({
                    'match_id': match.id,
                    'player_id': player.get('player_id'),
                    'kills': player.get('kills', 0),
                    'deaths': player.get('deaths', 0),
                    'score': player.get('score', 0),
                })

            match.start_match()

            return {'status': 'success', 'match_id': match.id}

        except Exception as e:
            return {'error': str(e)}
