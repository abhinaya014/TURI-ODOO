from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class GameSkinAPI(http.Controller):

    def _json_response(self, data, status=200):
        return request.make_response(
            json.dumps(data, default=str),
            headers={'Content-Type': 'application/json'},
            status=status
        )

    # ---------------------------
    # GET: Obtener todas las skins disponibles
    # ---------------------------
    @http.route('/game_api/skins', type='http', auth='public', methods=['GET'], csrf=False)
    def get_skins(self):
        try:
            skins = request.env['game.skin'].sudo().search([])
            skin_list = [{
                'id': skin.id,
                'name': skin.name,
                'image': skin.image,  # Devuelve la imagen como una ruta en el módulo
            } for skin in skins]

            return self._json_response({'status': 'success', 'skins': skin_list})

        except Exception as e:
            _logger.error(f"Error obteniendo skins: {e}")
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)

    # ---------------------------
    # GET: Obtener las skins de un jugador
    # ---------------------------
    @http.route('/game_api/skins/player/<int:player_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_player_skins(self, player_id):
        try:
            player = request.env['game.player'].sudo().browse(player_id)
            if not player.exists():
                return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

            skin_list = [{
                'id': skin.id,
                'name': skin.name,
                'type': skin.type
            } for skin in player.owned_by_players]  # FIX: Cambié owned_skins por owned_by_players

            return self._json_response({'status': 'success', 'player_id': player.id, 'skins': skin_list})

        except Exception as e:
            _logger.error(f"Error obteniendo skins del jugador: {e}")
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)

    # ---------------------------
    # POST: Comprar una skin
    # ---------------------------
    @http.route('/game_api/skins/buy', type='http', auth='public', methods=['POST'], csrf=False)
    def buy_skin(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f"Datos recibidos en compra de skin: {data}")

            player_id = data.get('player_id')
            skin_id = data.get('skin_id')
            skin_price = data.get('price', 50)  # Precio por defecto

            if not player_id or not skin_id:
                _logger.error("Faltan parámetros en la compra de skin (player_id, skin_id)")
                return self._json_response({'status': 'error', 'message': 'Faltan parámetros (player_id, skin_id)'}, 400)

            player = request.env['game.player'].sudo().browse(player_id)
            skin = request.env['game.skin'].sudo().browse(skin_id)

            if not player.exists():
                _logger.error(f"Jugador no encontrado con ID: {player_id}")
                return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

            if not skin.exists():
                _logger.error(f"Skin no encontrada con ID: {skin_id}")
                return self._json_response({'status': 'error', 'message': 'Skin no encontrada'}, 404)

            if skin in player.owned_by_players:  # FIX: Cambié owned_skins por owned_by_players
                _logger.error(f"El jugador {player_id} ya posee esta skin")
                return self._json_response({'status': 'error', 'message': 'Ya posees esta skin'}, 400)

            if player.coin_balance < skin_price:
                _logger.error(f"Saldo insuficiente: {player.coin_balance} < {skin_price}")
                return self._json_response({'status': 'error', 'message': 'Saldo insuficiente'}, 400)

            # Restar monedas y asignar la skin
            request.env['game.coin.transaction'].sudo().create({
                'player_id': player.id,
                'amount': -skin_price,
                'reason': f'Compra de skin {skin.name}'
            })

            player.sudo().write({
                'coin_balance': player.coin_balance - skin_price  # FIX: Ahora sí se resta el saldo
            })

            player.owned_by_players = [(4, skin.id)]  # FIX: owned_by_players en vez de owned_skins

            return self._json_response({
                'status': 'success',
                'message': f'Skin {skin.name} comprada',
                'new_balance': player.coin_balance
            })

        except Exception as e:
            _logger.error(f"Error comprando skin: {e}")
            return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)
