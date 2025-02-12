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

    @http.route('/game_api/coins/add', type='json', auth='public', methods=['POST'], csrf=False)
    def add_coins(self):
        try:
            data = request.jsonrequest  # Obtener JSON correctamente
            _logger.info(f"Datos recibidos en POST: {data}")  # LOG

            player_id = data.get('player_id')
            amount = data.get('amount')
            reason = data.get('reason', 'Recarga de monedas')

            if not player_id or amount is None:
                _logger.error("Faltan parámetros en POST (player_id, amount)")
                return {'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                _logger.error(f"Jugador no encontrado con ID: {player_id}")
                return {'status': 'error', 'message': 'Jugador no encontrado'}

            if amount <= 0:
                _logger.error("El monto debe ser mayor a 0")
                return {'status': 'error', 'message': 'El monto debe ser mayor a 0'}

            # Crear la transacción
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': amount,
                'reason': reason
            })

            _logger.info(f"Monedas agregadas correctamente. Nuevo saldo: {player.coin_balance}")
            return {'status': 'success', 'message': 'Monedas agregadas correctamente', 'new_balance': player.coin_balance}

        except Exception as e:
            _logger.error(f"Error agregando monedas: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': 'Error interno del servidor'}

    @http.route('/game_api/coins/use', type='json', auth='public', methods=['PUT'], csrf=False)
    def use_coins(self):
        try:
            data = request.jsonrequest  # Obtener JSON correctamente
            _logger.info(f"Datos recibidos en PUT: {data}")  # LOG

            player_id = data.get('player_id')
            amount = data.get('amount')
            reason = data.get('reason', 'Compra en el juego')

            if not player_id or amount is None:
                _logger.error("Faltan parámetros en PUT (player_id, amount)")
                return {'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                _logger.error(f"Jugador no encontrado con ID: {player_id}")
                return {'status': 'error', 'message': 'Jugador no encontrado'}

            if amount <= 0:
                _logger.error("El monto debe ser mayor a 0")
                return {'status': 'error', 'message': 'El monto debe ser mayor a 0'}

            if player.coin_balance < amount:
                _logger.error(f"Saldo insuficiente: {player.coin_balance} < {amount}")
                return {'status': 'error', 'message': 'Saldo insuficiente'}

            # Crear la transacción de gasto
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': -amount,
                'reason': reason
            })

            _logger.info(f"Compra realizada. Nuevo saldo: {player.coin_balance}")
            return {'status': 'success', 'message': 'Compra realizada', 'new_balance': player.coin_balance}

        except Exception as e:
            _logger.error(f"Error usando monedas: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': 'Error interno del servidor'}
