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
    # LOGIN DE JUGADOR
    # -----------------------------
    @http.route('/game_api/login', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def login_player(self):
        try:
            # Verificar si hay datos en la solicitud
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            # Cargar manualmente el JSON
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError as e:
                _logger.error(f"Error al decodificar JSON: {e}")
                return self._json_response({'status': 'error', 'message': 'Formato de JSON inválido'}, 400)

            _logger.info(f"Datos recibidos: {data}")

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

        except Exception as e:
            _logger.error(f"Error en el login del jugador: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)
