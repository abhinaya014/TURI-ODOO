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

    @http.route('/game_api/register', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def register_player(self):
        try:
            if not request.httprequest.data:
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío'}, 400)

            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return self._json_response({'status': 'error', 'message': 'Formato de JSON inválido'}, 400)

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios'}, 400)

            existing_player = request.env['game.player'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear un contacto en res.partner
            partner_vals = {'name': name, 'email': email}
            partner = request.env['res.partner'].sudo().create(partner_vals)

            # Crear el jugador y vincularlo al contacto
            player_vals = {'name': name, 'email': email, 'password': password, 'partner_id': partner.id}
            player = request.env['game.player'].sudo().create(player_vals)

            return self._json_response({
                'status': 'success',
                'message': 'Jugador registrado con éxito',
                'data': {
                    'player_id': player.id,
                    'name': player.name,
                    'email': player.email,
                    'partner_id': partner.id
                }
            })

        except Exception as e:
            _logger.error(f"Error en el registro del jugador: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)
