from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameCoinAPI(http.Controller):

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data, default=str),
            headers={'Content-Type': 'application/json'},
            status=status
        )

    # ---------------------------
    # GET: Obtener balance de monedas
    # ---------------------------
    @http.route('/game_api/coins/<int:player_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_coin_balance(self, player_id):
        try:
            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

            return self._json_response({
                'status': 'success',
                'player_id': player.id,
                'coin_balance': player.coin_balance
            })

        except Exception as e:
            _logger.error(f"Error obteniendo monedas: {e}")
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)

    # ---------------------------
    # POST: Agregar monedas al jugador
    # ---------------------------
    @http.route('/game_api/coins/add', type='json', auth='public', methods=['POST'], csrf=False)
    def add_coins(self, **kwargs):
        try:
            player_id = kwargs.get('player_id')
            amount = kwargs.get('amount')
            reason = kwargs.get('reason', 'Recarga de monedas')

            if not player_id or amount is None:
                return {'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                return {'status': 'error', 'message': 'Jugador no encontrado'}

            if amount <= 0:
                return {'status': 'error', 'message': 'El monto debe ser mayor a 0'}

            # Crear la transacción
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': amount,
                'reason': reason
            })

            return {'status': 'success', 'message': 'Monedas agregadas correctamente', 'new_balance': player.coin_balance}

        except Exception as e:
            _logger.error(f"Error agregando monedas: {e}")
            return {'status': 'error', 'message': 'Error interno del servidor'}

    # ---------------------------
    # PUT: Restar monedas cuando compra algo
    # ---------------------------
    @http.route('/game_api/coins/use', type='json', auth='public', methods=['PUT'], csrf=False)
    def use_coins(self, **kwargs):
        try:
            player_id = kwargs.get('player_id')
            amount = kwargs.get('amount')
            reason = kwargs.get('reason', 'Compra en el juego')

            if not player_id or amount is None:
                return {'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                return {'status': 'error', 'message': 'Jugador no encontrado'}

            if amount <= 0:
                return {'status': 'error', 'message': 'El monto debe ser mayor a 0'}

            if player.coin_balance < amount:
                return {'status': 'error', 'message': 'Saldo insuficiente'}

            # Crear la transacción de gasto
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': -amount,
                'reason': reason
            })

            return {'status': 'success', 'message': 'Compra realizada', 'new_balance': player.coin_balance}

        except Exception as e:
            _logger.error(f"Error usando monedas: {e}")
            return {'status': 'error', 'message': 'Error interno del servidor'}
