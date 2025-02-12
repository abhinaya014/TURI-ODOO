from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameMatchAPI(http.Controller):

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data, default=str),
            headers={'Content-Type': 'application/json'},
            status=status
        )

    # ---------------------------
    # POST: Crear un Match
    # ---------------------------
    @http.route('/game_api/match/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_match(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Datos recibidos en creación de match: {data}")

            match_name = data.get('name', 'Match_' + fields.Datetime.now().strftime('%Y%m%d%H%M%S'))
            state = data.get('state', 'draft')
            player_stats = data.get('players', [])  # Lista de jugadores con estadísticas

            if not player_stats:
                _logger.error("No se proporcionaron jugadores para el match")
                return self._json_response({'status': 'error', 'message': 'Debe haber al menos 2 jugadores en el match'}, 400)

            if len(player_stats) < 2:
                _logger.error("Menos de 2 jugadores en el match")
                return self._json_response({'status': 'error', 'message': 'Un match debe tener al menos 2 jugadores'}, 400)

            # Crear el match
            match = request.env['game.match'].sudo().create({
                'name': match_name,
                'state': state,
                'start_time': fields.Datetime.now() if state == 'in_progress' else None
            })

            # Crear estadísticas para cada jugador
            player_stat_records = []
            for player_stat in player_stats:
                player_id = player_stat.get('player_id')
                kills = player_stat.get('kills', 0)
                deaths = player_stat.get('deaths', 0)
                score = player_stat.get('score', 0)

                player = request.env['game.player'].sudo().browse(player_id)
                if not player.exists():
                    _logger.error(f"Jugador con ID {player_id} no encontrado")
                    return self._json_response({'status': 'error', 'message': f'Jugador con ID {player_id} no encontrado'}, 404)

                player_stat_records.append((0, 0, {
                    'player_id': player.id,
                    'kills': kills,
                    'deaths': deaths,
                    'score': score
                }))

            match.sudo().write({'player_stats_ids': player_stat_records})

            return self._json_response({
                'status': 'success',
                'message': 'Match creado con éxito',
                'match_id': match.id,
                'state': match.state
            })

        except Exception as e:
            _logger.error(f"Error creando match: {e}", exc_info=True)
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)
