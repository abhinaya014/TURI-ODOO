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

    # Registro de jugador
    @http.route('/game_api/register', type='json', auth='none', methods=['POST'], csrf=False, session_less=True)
    def register_player(self):
        try:
            # Obtener datos JSON
            data = request.jsonrequest

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                return self._json_response({'status': 'error', 'message': 'Faltan campos obligatorios'}, 400)

            # Verificar email único
            existing_player = request.env['game.player'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return self._json_response({'status': 'error', 'message': 'El email ya está registrado'}, 409)

            # Crear el jugador
            player = request.env['game.player'].sudo().create({
                'name': name,
                'email': email,
                'password': password,
            })

            return self._json_response({
                'status': 'success',
                'message': 'Jugador registrado con éxito',
                'data': {
                    'player_id': player.id,
                    'name': player.name,
                    'email': player.email,
                    'level': player.level,
                    'coin_balance': player.coin_balance
                }
            })

        except Exception as e:
            _logger.error(f"Error en el registro del jugador: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # Login de jugador
    @http.route('/game_api/login', type='json', auth='none', methods=['POST'], csrf=False, session_less=True)
    def login_player(self):
        try:
            data = request.jsonrequest
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return self._json_response({'status': 'error', 'message': 'Email y contraseña son obligatorios'}, 400)

            player = request.env['game.player'].sudo().search([('email', '=', email), ('password', '=', password)], limit=1)
            if not player:
                return self._json_response({'status': 'error', 'message': 'Email o contraseña incorrectos'}, 401)

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
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # -----------------------------
    # SKINS
    # -----------------------------
    @http.route('/game_api/skins', type='json', auth='public', methods=['GET'], csrf=False, session_less=True)
    def api_list_skins(self):
        try:
            skins = request.env['game.skin'].sudo().search([])
            data = [{
                'id': skin.id,
                'name': skin.name,
                'type': skin.type,
                'description': skin.description
            } for skin in skins]
            return self._json_response({'status': 'success', 'data': data})
        except Exception as e:
            _logger.error(f"Error al listar skins: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # -----------------------------
    # PARTIDOS
    # -----------------------------
    @http.route('/game_api/matches', type='json', auth='public', methods=['GET'], csrf=False, session_less=True)
    def api_list_matches(self):
        try:
            matches = request.env['game.match'].sudo().search([])
            data = [{
                'id': match.id,
                'name': match.name,
                'start_time': match.start_time,
                'end_time': match.end_time,
                'state': match.state,
                'winner_id': match.winner_id.id if match.winner_id else None,
                'score': match.score
            } for match in matches]
            return self._json_response({'status': 'success', 'data': data})
        except Exception as e:
            _logger.error(f"Error al listar partidos: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)

    # -----------------------------
    # TRANSACCIONES DE MONEDAS
    # -----------------------------
    @http.route('/game_api/transactions', type='json', auth='public', methods=['GET'], csrf=False, session_less=True)
    def api_list_transactions(self):
        try:
            transactions = request.env['game.coin.transaction'].sudo().search([])
            data = [{
                'id': t.id,
                'player_id': t.player_id.id,
                'amount': t.amount,
                'reason': t.reason,
                'date': t.date
            } for t in transactions]
            return self._json_response({'status': 'success', 'data': data})
        except Exception as e:
            _logger.error(f"Error al listar transacciones: {e}")
            return self._json_response({'status': 'error', 'message': str(e)}, 500)
