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
                'image': skin.image
            } for skin in player.owned_by_players]

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
            return self._json_response({'status': 'error', 'message': 'Faltan parámetros (player_id, skin_id)'}, 400)

        player = request.env['game.player'].sudo().browse(player_id)
        skin = request.env['game.skin'].sudo().browse(skin_id)

        if not player.exists():
            return self._json_response({'status': 'error', 'message': 'Jugador no encontrado'}, 404)

        if not skin.exists():
            return self._json_response({'status': 'error', 'message': 'Skin no encontrada'}, 404)

        if skin in player.owned_skins:
            return self._json_response({'status': 'error', 'message': 'Ya posees esta skin'}, 400)

        # ✅ Asegurar que el saldo está actualizado antes de hacer la resta
        player.sudo().flush()  # 🛠️ Forzar actualización de datos antes de leer `coin_balance`
        current_balance = player.coin_balance

        if current_balance < skin_price:
            return self._json_response({'status': 'error', 'message': 'Saldo insuficiente'}, 400)

        # ✅ Registrar la transacción de monedas en game.coin.transaction
        request.env['game.coin.transaction'].sudo().create({
            'player_id': player.id,
            'amount': -skin_price,
            'reason': f'Compra de skin {skin.name}'
        })

        # ✅ Restar monedas del saldo del jugador usando el saldo actualizado
        new_balance = current_balance - skin_price  # 🛠️ Asegurar que siempre usa el valor correcto
        player.sudo().write({'coin_balance': new_balance})

        # ✅ Agregar la skin al jugador manteniendo las anteriores
        player.sudo().write({
            'owned_skins': [(4, skin.id)]
        })

        return self._json_response({
            'status': 'success',
            'message': f'Skin {skin.name} comprada con éxito',
            'new_balance': new_balance
        })

    except Exception as e:
        _logger.error(f"Error comprando skin: {e}")
        return self._json_response({'status': 'error', 'message': 'Error interno del servidor'}, 500)
