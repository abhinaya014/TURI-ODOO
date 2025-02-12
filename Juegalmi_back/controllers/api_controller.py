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

            login_identifier = data.get('login')  # Puede ser email o username
            password = data.get('password')

            # Validaciones básicas
            if not login_identifier or not password:
                return self._json_response({'status': 'error', 'message': 'Login y contraseña son obligatorios'}, 400)

            # Buscar el jugador por email o username
            player = request.env['game.player'].sudo().search([
                '|',
                ('email', '=', login_identifier),
                ('name', '=', login_identifier),
                ('password', '=', password)
            ], limit=1)

            if not player:
                return self._json_response({'status': 'error', 'message': 'Login o contraseña incorrectos'}, 401)

            # Actualizar la última fecha de login
            player.sudo().write({'last_login': fields.Datetime.now()})

            # Obtener skins compradas
            skins = [{
                'id': skin.id,
                'name': skin.name,
                'color': skin.color,
                'photo': f"data:image/png;base64,{skin.photo.decode('utf-8')}" if skin.photo else None
            } for skin in player.owned_skins]

            # Respuesta exitosa con skins incluidas
            return self._json_response({
                'status': 'success',
                'message': 'Login exitoso',
                'data': {
                    'id': player.id,
                    'name': player.name,
                    'email': player.email,
                    'coin_balance': player.coin_balance,
                    'level': player.level,
                    'last_login': player.last_login,
                    'skins': skins  # Lista de skins compradas
                }
            })

        except Exception as e:
            _logger.error(f"Error en el login del jugador: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)
