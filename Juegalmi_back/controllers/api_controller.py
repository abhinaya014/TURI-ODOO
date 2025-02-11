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
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError as e:
                _logger.error(f"Error al decodificar JSON: {e}")
                return self._json_response({'status': 'error', 'message': 'Formato de JSON inválido'}, 400)

            _logger.info(f"Datos recibidos: {data}")

            login_identifier = data.get('login')  # Corregido
            password = data.get('password')

            if not login_identifier or not password:
                return self._json_response({'status': 'error', 'message': 'Login y contraseña son obligatorios'}, 400)

            player = request.env['res.partner'].sudo().search([
                '|',
                ('email', '=', login_identifier),
                ('name', '=', login_identifier)
            ], limit=1)

            if player and player.password == password:
                player.sudo().write({'last_login': fields.Datetime.now()})  # Actualiza la fecha de login

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
            else:
                return self._json_response({'status': 'error', 'message': 'Login o contraseña incorrectos'}, 401)

        except Exception as e:
            _logger.error(f"Error en el login del jugador: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)

    # -----------------------------
    # REGISTRO DE JUGADOR
    # -----------------------------
    @http.route('/game_api/register', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def register_player(self):
        try:
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError as e:
                _logger.error(f"Error al decodificar JSON: {e}")
                return self._json_response({'status': 'error', 'message': 'Formato de JSON inválido'}, 400)

            _logger.info(f"Datos recibidos para el registro: {data}")

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios (name, email, password)'}, 400)

            existing_player = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear el jugador sin incluir el campo 'password' directamente
            player_vals = {
                'name': name,
                'email': email
            }
            player = request.env['res.partner'].sudo().create(player_vals)

            # Establecer el password luego de crear el registro
            player.sudo().write({'password': password})

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
