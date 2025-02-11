from odoo import http
from odoo.http import request
import json

class UnityMatchController(http.Controller):

    @http.route('/api/match', type='http', auth='public', methods=['POST'], csrf=False)
    def create_match(self, **kwargs):
        try:
            # Leer el cuerpo de la solicitud manualmente
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Verificar los datos recibidos
            print("Datos recibidos:", json.dumps(data, indent=4))

            # Validar los datos esperados
            name = data.get('name')
            players = data.get('players')

            if not name or not players or len(players) < 2:
                return http.Response(
                    json.dumps({'error': 'El nombre del partido y al menos 2 jugadores son obligatorios.'}),
                    status=400,
                    content_type='application/json'
                )

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

            return http.Response(
                json.dumps({'status': 'success', 'match_id': match.id}),
                status=200,
                content_type='application/json'
            )

        except Exception as e:
            return http.Response(
                json.dumps({'error': str(e)}),
                status=500,
                content_type='application/json'
            )
