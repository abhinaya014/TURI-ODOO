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
    # POST: Agregar monedas al jugador
    # ---------------------------
    @http.route('/game_api/coins/add', type='http', auth='public', methods=['POST'], csrf=False)
    def add_coins(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))  # 🔥 Leer JSON manualmente
            _logger.info(f"Datos recibidos en POST: {data}")  # LOG

            player_id = data.get('player_id')
            amount = data.get('amount')
            reason = data.get('reason', 'Recarga de monedas')

            if not player_id or amount is None:
                _logger.error("Faltan parámetros en POST (player_id, amount)")
                return self._json_response({'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}, 400)

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                _logger.error(f"Jugador no encontrado con ID: {player_id}")
                return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

            if amount <= 0:
                _logger.error("El monto debe ser mayor a 0")
                return self._json_response({'status': 'error', 'message': 'El monto debe ser mayor a 0'}, 400)

            # Crear la transacción
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': amount,
                'reason': reason
            })

            return self._json_response({'status': 'success', 'message': 'Monedas agregadas correctamente', 'new_balance': player.coin_balance})

        except Exception as e:
            _logger.error(f"Error agregando monedas: {str(e)}", exc_info=True)
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)

    # ---------------------------
    # PUT: Restar monedas cuando compra algo
    # ---------------------------
    @http.route('/game_api/coins/use', type='http', auth='public', methods=['PUT'], csrf=False)
    def use_coins(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))  # 🔥 Leer JSON manualmente
            _logger.info(f"Datos recibidos en PUT: {data}")  # LOG

            player_id = data.get('player_id')
            amount = data.get('amount')
            reason = data.get('reason', 'Compra en el juego')

            if not player_id or amount is None:
                _logger.error("Faltan parámetros en PUT (player_id, amount)")
                return self._json_response({'status': 'error', 'message': 'Faltan parámetros (player_id, amount)'}, 400)

            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                _logger.error(f"Jugador no encontrado con ID: {player_id}")
                return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

            if amount <= 0:
                _logger.error("El monto debe ser mayor a 0")
                return self._json_response({'status': 'error', 'message': 'El monto debe ser mayor a 0'}, 400)

            if player.coin_balance < amount:
                _logger.error(f"Saldo insuficiente: {player.coin_balance} < {amount}")
                return self._json_response({'status': 'error', 'message': 'Saldo insuficiente'}, 400)

            # Crear la transacción de gasto
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': -amount,
                'reason': reason
            })

            return self._json_response({'status': 'success', 'message': 'Compra realizada', 'new_balance': player.coin_balance})

        except Exception as e:
            _logger.error(f"Error usando monedas: {str(e)}", exc_info=True)
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)
