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
    @http.route('/game_api/login', type='json', auth='public', methods=['POST'], csrf=False, session_less=True)
    def login_player(self):
        try:
            # Verificamos si el cuerpo de la solicitud tiene contenido JSON válido
            if not request.jsonrequest:
                _logger.error("El cuerpo de la solicitud no contiene datos JSON.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud no es JSON válido'}, 400)

            # Obtener los datos JSON
            data = request.jsonrequest
            _logger.info(f"Datos recibidos: {data}")

            email = data.get('email')
            password = data.get('password')

            # Validaciones básicas
            if not email or not password:
                _logger.warning("Faltan campos obligatorios: email o contraseña.")
                return self._json_response({'status': 'error', 'message': 'Email y contraseña son obligatorios'}, 400)

            # Buscar el jugador
            player = request.env['game.player'].sudo().search([('email', '=', email), ('password', '=', password)], limit=1)
            if not player:
                _logger.warning(f"Jugador no encontrado: {email}")
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
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor: ' + str(e)}, 500)
