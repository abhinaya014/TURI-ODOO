from odoo import http
from odoo.http import request
import json

class UnityMatchController(http.Controller):

    @http.route('/api/match', type='json', auth='public', methods=['POST'])
    def create_match(self):
        try:
            # Paso 1: Verificar si llegan los datos JSON correctamente
            data = request.httprequest.get_json()  # Obtener datos directamente
            print("Datos recibidos:", json.dumps(data, indent=4))

            # Validar si los datos esperados están presentes
            if not data:
                return {'error': 'No se recibieron datos.'}

            name = data.get('name')
            players = data.get('players')

            if not name or not players or len(players) < 2:
                return {'error': 'El nombre del partido y al menos 2 jugadores son obligatorios.'}

            # Respuesta temporal de prueba
            return {'status': 'success', 'message': 'Datos recibidos correctamente', 'data': data}

        except Exception as e:
            return {'error': str(e)}
