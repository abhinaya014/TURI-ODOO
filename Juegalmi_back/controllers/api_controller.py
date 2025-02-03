from odoo import http
from odoo.http import request, Response
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class GameAPIController(http.Controller):

    def _json_response(self, data, status=200):
        return Response(json.dumps(data, default=str), status=status, content_type='application/json')

    # Ejemplo de endpoint para listar jugadores
    @http.route('/game_api/players', type='json', auth='public', methods=['GET'], csrf=False)
    def api_list_players(self, **kwargs):
        players = request.env['game.player'].sudo().search([])
        data = [{
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'coin_balance': p.coin_balance,
        } for p in players]
        return {'status': 'success', 'data': data}

    # Aquí se pueden agregar más endpoints para skins, partidos y transacciones.
