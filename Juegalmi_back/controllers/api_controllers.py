from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data, default=str),
            headers={'Content-Type': 'application/json'},
            status=status
        )

    # -----------------------------
    # REGISTRO DE JUGADOR
    # -----------------------------
    @http.route('/game_api/register', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def register_player(self):
        try:
            # Verificamos si el cuerpo de la solicitud tiene contenido JSON válido
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            # Cargar manualmente el JSON
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError as e:
                _logger.error(f"Error al decodificar JSON: {e}")
                return self._json_response({'status': 'error', 'message': 'Formato de JSON inválido'}, 400)

            _logger.info(f"Datos recibidos para el registro: {data}")

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            # Validaciones básicas
            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios (name, email, password)'}, 400)

            # Comprobar si el email ya está registrado
            existing_player = request.env['game.player'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear el jugador
            player_vals = {
                'name': name,
                'email': email,
                'password': password
            }
            player = request.env['game.player'].sudo().create(player_vals)

            # Respuesta exitosa
            return self._json_response({
                'status': 'success',
                'message': 'Jugador registrado con éxito',
                'data': {
                    'player_id': player.id,
                    'name': player.name,
                    'email': player.email,
                    'level': player.level,
                    'coin_balance': player.coin_balance,
                    'registration_date': player.registration_date
                }
            })

        except Exception as e:
            _logger.error(f"Error en el registro del jugador: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)
