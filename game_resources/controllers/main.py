from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):

    @http.route('/game_resources/api/players2', type='http', auth='none', csrf=False, cors='*', methods=['POST', 'GET'])    
    def get_players(self):
        if request.httprequest.method == 'GET':
            return {
                'status': 'success',
                'message': 'GET request received'
            }
        elif request.httprequest.method == 'POST':
            data = request.jsonrequest
            return {
                'status': 'success',
                'data': data
            }
        return {
            'status': 'error',
            'message': 'Unsupported method'
        }

    def _json_response(self, data, status=200):
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return None

        return Response(
            json.dumps(data, default=datetime_handler),
            status=status,
            headers=[('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type, Authorization')]
        )

    @http.route('/game_resources/api/test', type='http', auth='none', csrf=False, cors='*')
    def test_connection(self):
        try:
            return self._json_response({
                'status': 'success',
                'message': 'API is working!',
                'timestamp': str(datetime.now())
            })
        except Exception as e:
            _logger.error("Test endpoint error: %s", str(e))
            return self._json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)

    @http.route('/game_resources/api/players', type='json', auth='none', csrf=False, cors='*')
    def players(self, **kwargs):
        method = request.httprequest.method
        try:
            if method == 'GET':
                return self.list_players()
            elif method == 'POST':
                return self.create_player()
            else:
                return self._json_response({
                    'status': 'error',
                    'message': f'Method {method} not allowed'
                }, status=405)
        except Exception as e:
            _logger.error(f"Players endpoint error: {str(e)}")
            return self._json_response({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    @http.route('/game_resources/api/players/<int:player_id>', type='http', auth='none', csrf=False, cors='*')
    def player_by_id(self, player_id, **kwargs):
        method = request.httprequest.method
        try:
            if method == 'GET':
                return self.get_player(player_id)
            elif method == 'PUT':
                return self.update_player(player_id)
            elif method == 'DELETE':
                return self.delete_player(player_id)
            else:
                return self._json_response({
                    'status': 'error',
                    'message': f'Method {method} not allowed'
                }, status=405)
        except Exception as e:
            _logger.error(f"Player by ID endpoint error: {str(e)}")
            return self._json_response({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    def list_players(self):
        players = request.env['game.player'].sudo().search([])
        player_list = [{
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'level': p.level,
            'experience': p.experience,
            'active': p.active,
            'registration_date': p.registration_date,
            'last_login': p.last_login
        } for p in players]

        return self._json_response({
            'status': 'success',
            'data': player_list
        })

    def create_player(self):
        data = json.loads(request.httprequest.data)
        required_fields = ['name', 'email', 'password']
        
        if not all(field in data for field in required_fields):
            return self._json_response({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)

        existing_player = request.env['game.player'].sudo().search([
            '|',
            ('name', '=', data['name']),
            ('email', '=', data['email'])
        ])
        
        if existing_player:
            return self._json_response({
                'status': 'error',
                'message': 'Username or email already exists'
            }, status=409)

        player = request.env['game.player'].sudo().create({
            'name': data['name'],
            'email': data['email'],
            'password': data['password']
        })

        return self._json_response({
            'status': 'success',
            'data': {
                'id': player.id,
                'name': player.name,
                'email': player.email,
                'registration_date': player.registration_date
            }
        }, status=201)

    def get_player(self, player_id):
        player = request.env['game.player'].sudo().browse(player_id)
        if not player.exists():
            return self._json_response({
                'status': 'error',
                'message': 'Player not found'
            }, status=404)

        return self._json_response({
            'status': 'success',
            'data': {
                'id': player.id,
                'name': player.name,
                'email': player.email,
                'level': player.level,
                'experience': player.experience,
                'registration_date': player.registration_date,
                'last_login': player.last_login,
                'active': player.active
            }
        })

    def update_player(self, player_id):
        player = request.env['game.player'].sudo().browse(player_id)
        if not player.exists():
            return self._json_response({
                'status': 'error',
                'message': 'Player not found'
            }, status=404)

        data = json.loads(request.httprequest.data)
        allowed_fields = ['email', 'password', 'active']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return self._json_response({
                'status': 'error',
                'message': 'No valid fields to update'
            }, status=400)

        player.write(update_data)

        return self._json_response({
            'status': 'success',
            'data': {
                'id': player.id,
                'name': player.name,
                'email': player.email,
                'active': player.active
            }
        })

    def delete_player(self, player_id):
        player = request.env['game.player'].sudo().browse(player_id)
        if not player.exists():
            return self._json_response({
                'status': 'error',
                'message': 'Player not found'
            }, status=404)

        player.write({'active': False})

        return self._json_response({
            'status': 'success',
            'message': 'Player deactivated successfully'
        })