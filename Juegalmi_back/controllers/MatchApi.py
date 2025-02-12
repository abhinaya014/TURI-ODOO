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
    # POST: Crear Match desde Unity
    # ---------------------------
    @http.route('/game_api/match/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_match(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Datos recibidos en creación de match desde Unity: {data}")

            player_stats = data.get('players', [])
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            if not player_stats or len(player_stats) < 2:
                _logger.error("Debe haber al menos 2 jugadores en el match")
                return self._json_response({'status': 'error', 'message': 'Debe haber al menos 2 jugadores en el match'}, 400)

            if not start_time or not end_time:
                _logger.error("Faltan fecha de inicio o fin")
                return self._json_response({'status': 'error', 'message': 'Debe haber fecha de inicio y fin'}, 400)

            # Convertir fechas a formato datetime de Odoo
            start_time = fields.Datetime.from_string(start_time)
            end_time = fields.Datetime.from_string(end_time)

            # Crear el match
            match = request.env['game.match'].sudo().create({
                'name': f'Match_{fields.Datetime.now().strftime("%Y%m%d%H%M%S")}',
                'state': 'finished',
                'start_time': start_time,
                'end_time': end_time
            })

            # Determinar el ganador basado en el jugador con más kills
            winner = None
            winner_kills = -1
            winner_score = 0
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

                # Registrar estadísticas del jugador en el match
                player_stat_records.append((0, 0, {
                    'player_id': player.id,
                    'kills': kills,
                    'deaths': deaths,
                    'score': score
                }))

                # Verificar si este jugador tiene más kills y es el nuevo ganador
                if kills > winner_kills:
                    winner = player
                    winner_kills = kills
                    winner_score = score

            # Asignar estadísticas al match
            match.sudo().write({'player_stats_ids': player_stat_records})

            # Asignar el ganador si se encontró
            if winner:
                match.sudo().write({
                    'winner_id': winner.id,
                    'score': winner_score
                })
                _logger.info(f"Ganador del match: {winner.name} con {winner_kills} kills y {winner_score} puntos")

            return self._json_response({
                'status': 'success',
                'message': 'Match creado con éxito',
                'match_id': match.id,
                'winner_id': winner.id if winner else None,
                'winner_name': winner.name if winner else None,
                'winner_score': winner_score
            })

        except Exception as e:
            _logger.error(f"Error creando match: {e}", exc_info=True)
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)
