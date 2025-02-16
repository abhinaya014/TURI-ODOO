from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta

class GameDashboardController(http.Controller):

    @http.route('/game/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        # Obtener datos para KPIs
        total_players = request.env['game.player'].search_count([])
        total_matches = request.env['game.match'].search_count([])
        total_skins = request.env['game.skin'].search_count([])
        total_coins = sum(request.env['game.player'].search([]).mapped('coin_balance'))

        # Datos para el gráfico de distribución de skins
        skins = request.env['game.skin'].search([])
        skin_data = {
            'labels': skins.mapped('name'),
            'data': [len(skin.owned_by_players) for skin in skins]
        }

        # Datos para el top de jugadores
        players = request.env['game.player'].search([], limit=10, order='total_wins desc')
        player_data = {
            'labels': players.mapped('name'),
            'data': players.mapped('total_wins')
        }

        # Datos para la actividad de partidas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        matches = request.env['game.match'].search([
            ('start_time', '>=', start_date),
            ('start_time', '<=', end_date)
        ])

        # Agrupar partidas por día
        match_data = {}
        for match in matches:
            date_str = match.start_time.strftime('%Y-%m-%d')
            match_data[date_str] = match_data.get(date_str, 0) + 1

        # Crear arrays para el gráfico
        dates = []
        match_counts = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            dates.append(date_str)
            match_counts.append(match_data.get(date_str, 0))
            current_date += timedelta(days=1)

        return {
            'kpis': {
                'total_players': total_players,
                'total_matches': total_matches,
                'total_skins': total_skins,
                'total_coins': total_coins,
            },
            'skin_distribution': skin_data,
            'top_players': player_data,
            'match_activity': {
                'labels': dates,
                'data': match_counts
            }
        }