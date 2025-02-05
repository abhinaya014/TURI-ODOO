from odoo import http, fields
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):

    def _json_response(self, data, status=200):
        return Response(json.dumps(data, default=str), status=status, content_type='application/json')

    # LISTAR JUGADORES
    @http.route('/game_api/players', type='json', auth='public', methods=['GET'], csrf=False)
    def api_list_players(self, **kwargs):
        players = request.env['game.player'].sudo().search([])
        data = [{
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'coin_balance': p.coin_balance,
        } for p in players]
        return self._json_response({'status': 'success', 'data': data})

    # REGISTRO DE JUGADOR
    @http.route('/game_api/register', type='json', auth='none', methods=['POST'], csrf=False)
    def register_player(self, **kwargs):
        try:
            name = kwargs.get('name')
            email = kwargs.get('email')
            password = kwargs.get('password')
            photo = kwargs.get('photo')  # Base64 string para la foto (opcional)

            # Validaciones básicas
            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios'}, 400)

            # Comprobar si ya existe un jugador con el mismo email
            existing_player = request.env['game.player'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear el jugador
            player_vals = {
                'name': name,
                'email': email,
                'password': password,
            }
            if photo:
                player_vals['photo'] = photo  # Se asume que es una cadena en Base64

            player = request.env['game.player'].sudo().create(player_vals)

            # Respuesta de éxito
            return self._json_response({
                'status': 'success',
                'message': 'Jugador registrado con éxito',
                'player_id': player.id
            })

        except Exception as e:
            _logger.error(f"Error en el registro del jugador: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # LOGIN DE JUGADOR
    @http.route('/game_api/login', type='json', auth='none', methods=['POST'], csrf=False)
    def login_player(self, **kwargs):
        try:
            email = kwargs.get('email')
            password = kwargs.get('password')

            # Validaciones básicas
            if not email or not password:
                return self._json_response({'status': 'error', 'message': 'Email y contraseña son obligatorios'}, 400)

            # Buscar el jugador
            player = request.env['game.player'].sudo().search([('email', '=', email), ('password', '=', password)], limit=1)
            if not player:
                return self._json_response({'status': 'error', 'message': 'Email o contraseña incorrectos'}, 401)

            # Actualizar la última fecha de login
            player.sudo().write({'last_login': fields.Datetime.now()})

            # Respuesta exitosa con los datos del jugador
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
            return self._json_response({'status': 'error', 'message': str(e)}, 500)
