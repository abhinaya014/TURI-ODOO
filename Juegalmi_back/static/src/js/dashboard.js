odoo.define('juegalmi_back.dashboard', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var KanbanRecord = require('web.KanbanRecord');
    var view_registry = require('web.view_registry');
    var core = require('web.core');

    var GameDashboardRecord = KanbanRecord.extend({
        events: _.extend({}, KanbanRecord.prototype.events, {
            'click .refresh-stats': '_onRefreshStats',
        }),

        start: async function () {
            await this._super.apply(this, arguments);
            this._renderCharts();
        },

        _renderCharts: async function () {
            const playerId = this.recordData.id;
            
            // Obtener datos del jugador
            const playerData = await this._rpc({
                model: 'game.player',
                method: 'get_player_statistics',
                args: [playerId]
            });

            // Gráfica de Estadísticas
            new Chart(document.getElementById(`player-stats-chart-${playerId}`), {
                type: 'bar',
                data: {
                    labels: ['Kills', 'Deaths', 'Wins', 'Matches'],
                    datasets: [{
                        label: 'Player Statistics',
                        data: [
                            playerData.total_kills,
                            playerData.total_deaths,
                            playerData.total_wins,
                            playerData.total_matches
                        ],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(54, 162, 235, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Player Performance'
                        }
                    }
                }
            });

            // Gráfica de Monedas
            new Chart(document.getElementById(`coins-chart-${playerId}`), {
                type: 'line',
                data: {
                    labels: playerData.coin_history.dates,
                    datasets: [{
                        label: 'Coin Balance',
                        data: playerData.coin_history.balances,
                        borderColor: 'rgb(255, 206, 86)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            // Gráfica de Skins
            new Chart(document.getElementById(`skins-chart-${playerId}`), {
                type: 'doughnut',
                data: {
                    labels: playerData.skins_data.names,
                    datasets: [{
                        data: playerData.skins_data.counts,
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 206, 86)',
                            'rgb(75, 192, 192)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        },
    });

    var GameDashboardView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanController,
            Record: GameDashboardRecord,
        }),
    });

    view_registry.add('game_dashboard', GameDashboardView);

    return GameDashboardView;
});