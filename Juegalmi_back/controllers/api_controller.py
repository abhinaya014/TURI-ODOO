from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):

    def _json_response(self, data, status=200):
        return request.make_response(json.dumps(data, default=str), headers={'Content-Type': 'application/json'}, status=status)

    # -----------------------------
    # JUGADORES
    # -----------------------------

    # Listar jugadores
    @http.route('/game_api/players', type='json', auth='public', methods=['GET'], csrf=False, session_less=True)
    def api_list_players(self):
        try:
            players = request.env['game.player'].sudo().search([])
            data = [{
                'id': p.id,
                'name': p.name,
                'email': p.email,
                'coin_balance': p.coin_balance,
                'level': p.level
            } for p in players]
            return self._json_response({'status': 'success', 'data': data})
        except Exception as e:
            _logger.error(f"Error al listar jugadores: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # -----------------------------
    # LOGIN DE JUGADOR
    # -----------------------------
    @http.route('/game_api/login', type='json', auth='none', methods=['POST'], csrf=False, session_less=True)
    def login_player(self):
        try:
            # Obtener los datos JSON directamente del request
            data = request.jsonrequest  # Esto debería funcionar bien con POST en formato JSON

            email = data.get('email')
            password = data.get('password')

            # Validaciones básicas
            if not email or not password:
                return self._json_response({'status': 'error', 'message': 'Email y contraseña son obligatorios'}, 400)

            # Buscar el jugador
            player = request.env['game.player'].sudo().search([('email', '=', email), ('password', '=', password)], limit=1)
            if not player:
                return self._json_response({'status': 'error', 'message': 'Email o contraseña incorrectos'}, 401)

            # Actualizar la última fecha de login
            player.sudo().write({'last_login': fields.Datetime.now()})

            # Respuesta exitosa
            return self._json_response({
                'status': 'success',
                'message': 'Login exitoso',
                'data': {
                    'id': player.id,
                    'name': player.name,
                    'email': player.email,
                    'coin_balance': player.coin_balance,
                    'level': player.level,
                    'last_login': player.last_login
                }
            })

        except AttributeError as e:
            _logger.error(f"Error de atributo: {e}")
            return self._json_response({'status': 'error', 'message': f'Error al procesar la solicitud: {str(e)}'}, 400)
        except Exception as e:
            _logger.error(f"Error en el login del jugador: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)
