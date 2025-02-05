from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):
    # -----------------------------
    # JUGADORES
    # -----------------------------

    # Listar jugadores
    @http.route('/game_api/players', type='json', auth='public', methods=['GET'], csrf=False)
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
            return {'status': 'success', 'data': data}
        except Exception as e:
            _logger.error(f"Error al listar jugadores: {e}")
            return {'status': 'error', 'message': str(e)}

    # Registro de jugador
    @http.route('/game_api/register', type='json', auth='none', methods=['POST'], csrf=False)
    def register_player(self, **post):
        try:
            name = post.get('name')
            email = post.get('email')
            password = post.get('password')
            photo = post.get('photo')

            if not name or not email or not password:
                return {'status': 'error', 'message': 'Faltan campos obligatorios'}

            existing_player = request.env['game.player'].sudo().search([('email', '=', email)], limit=1)
            if existing_player:
                return {'status': 'error', 'message': 'El email ya está registrado'}

            player_vals = {'name': name, 'email': email, 'password': password}
            if photo:
                player_vals['photo'] = photo

            player = request.env['game.player'].sudo().create(player_vals)

            return {
                'status': 'success',
                'message': 'Jugador registrado con éxito',
                'player_id': player.id
            }

        except Exception as e:
            _logger.error(f"Error en el registro del jugador: {e}")
            return {'status': 'error', 'message': str(e)}

    # Login de jugador
    @http.route('/game_api/login', type='json', auth='none', methods=['POST'], csrf=False)
    def login_player(self, **post):
        try:
            email = post.get('email')
            password = post.get('password')

            if not email or not password:
                return {'status': 'error', 'message': 'Email y contraseña son obligatorios'}

            player = request.env['game.player'].sudo().search([('email', '=', email), ('password', '=', password)], limit=1)
            if not player:
                return {'status': 'error', 'message': 'Email o contraseña incorrectos'}

            player.sudo().write({'last_login': fields.Datetime.now()})

            return {
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
            }

        except Exception as e:
            _logger.error(f"Error en el login del jugador: {e}")
            return {'status': 'error', 'message': str(e)}

    # -----------------------------
    # SKINS
    # -----------------------------
    @http.route('/game_api/skins', type='json', auth='public', methods=['GET'], csrf=False)
    def api_list_skins(self):
        try:
            skins = request.env['game.skin'].sudo().search([])
            data = [{
                'id': skin.id,
                'name': skin.name,
                'type': skin.type,
                'description': skin.description
            } for skin in skins]
            return {'status': 'success', 'data': data}
        except Exception as e:
            _logger.error(f"Error al listar skins: {e}")
            return {'status': 'error', 'message': str(e)}

    # -----------------------------
    # PARTIDOS
    # -----------------------------
    @http.route('/game_api/matches', type='json', auth='public', methods=['GET'], csrf=False)
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
            return {'status': 'success', 'data': data}
        except Exception as e:
            _logger.error(f"Error al listar partidos: {e}")
            return {'status': 'error', 'message': str(e)}

    # -----------------------------
    # TRANSACCIONES DE MONEDAS
    # -----------------------------
    @http.route('/game_api/transactions', type='json', auth='public', methods=['GET'], csrf=False)
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
            return {'status': 'success', 'data': data}
        except Exception as e:
            _logger.error(f"Error al listar transacciones: {e}")
            return {'status': 'error', 'message': str(e)}