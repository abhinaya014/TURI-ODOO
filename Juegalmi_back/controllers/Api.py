from odoo import http
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
    # REGISTRO USANDO res.users
    # -----------------------------
    @http.route('/game_api/register', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def register_user(self):
        try:
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Datos recibidos para el registro: {data}")

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios (name, email, password)'}, 400)

            # Comprobar si el email ya existe en res.users
            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear usuario en res.users
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password
            })

            return self._json_response({
                'status': 'success',
                'message': 'Usuario registrado con éxito',
                'data': {
                    'user_id': new_user.id,
                    'name': new_user.name,
                    'email': new_user.login
                }
            })

        except Exception as e:
            _logger.error(f"Error en el registro: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)

    # -----------------------------
    # LOGIN USANDO res.users
    # -----------------------------
    @http.route('/game_api/login', type='http', auth='none', methods=['POST'], csrf=False, session_less=True)
    def login_user(self):
        try:
            if not request.httprequest.data:
                _logger.error("El cuerpo de la solicitud está vacío.")
                return self._json_response({'status': 'error', 'message': 'El cuerpo de la solicitud está vacío o no es JSON válido'}, 400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Datos recibidos para login: {data}")

            login_identifier = data.get('login')
            password = data.get('password')

            if not login_identifier or not password:
                return self._json_response({'status': 'error', 'message': 'Login y contraseña son obligatorios'}, 400)

            # Autenticación usando res.users
            user = request.env['res.users'].sudo().search([('login', '=', login_identifier)], limit=1)
            if not user or not user._check_password(password):
                return self._json_response({'status': 'error', 'message': 'Login o contraseña incorrectos'}, 401)

            # Autenticación exitosa, retornar datos del usuario
            return self._json_response({
                'status': 'success',
                'message': 'Login exitoso',
                'data': {
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.login
                }
            })

        except Exception as e:
            _logger.error(f"Error en el login: {e}")
            return self._json_response({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, 500)
