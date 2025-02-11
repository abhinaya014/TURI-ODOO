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
            data = request.jsonrequest  # Usar jsonrequest para obtener el cuerpo correctamente

            login_identifier = data.get('login')  # Puede ser email o username
            password = data.get('password')

            if not login_identifier or not password:
                return self._json_response({'status': 'error', 'message': 'Login y contraseña son obligatorios'}, 400)

            player = request.env['res.partner'].sudo().search([
                '|',
                ('email', '=', login_identifier),
                ('name', '=', login_identifier)
            ], limit=1)

            # Validar el password manualmente
            if not player or player.password != password:
                return self._json_response({'status': 'error', 'message': 'Login o contraseña incorrectos'}, 401)

            player.sudo().write({'last_login': fields.Datetime.now()})

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