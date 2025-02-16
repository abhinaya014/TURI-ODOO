odoo.define('juegalmi_back.dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');

    var GameDashboard = AbstractAction.extend({
        template: 'GameDashboard',
        events: {
            'click .refresh-stats': '_onRefreshStats',
        },

        init: function(parent, action) {
            this._super.apply(this, arguments);
        },

        start: async function() {
            await this._super(...arguments);
            this.renderCharts();
        },

        async renderCharts() {
            const stats = await this._loadStatistics();
            
            // Performance Chart
            new Chart(document.getElementById('main-stats-' + this.id), {
                type: 'bar',
                data: {
                    labels: ['Kills', 'Deaths', 'Wins', 'Matches'],
                    datasets: [{
                        data: [
                            stats.total_kills,
                            stats.total_deaths,
                            stats.total_wins,
                            stats.total_matches
                        ],
                        backgroundColor: [
                            '#4CAF50',
                            '#f44336',
                            '#2196F3',
                            '#FFC107'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });

            // Coin History Chart
            new Chart(document.getElementById('coin-history-' + this.id), {
                type: 'line',
                data: {
                    labels: stats.coin_history.dates,
                    datasets: [{
                        label: 'Balance',
                        data: stats.coin_history.balances,
                        borderColor: '#FFC107',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            // Skins Chart
            new Chart(document.getElementById('skins-chart-' + this.id), {
                type: 'doughnut',
                data: {
                    labels: stats.skins_data.names,
                    datasets: [{
                        data: stats.skins_data.counts,
                        backgroundColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FFC107',
                            '#f44336'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        },

        async _loadStatistics() {
            return await this._rpc({
                model: 'game.player',
                method: 'get_player_statistics',
                args: [this.id]
            });
        },

        _onRefreshStats: function(ev) {
            ev.preventDefault();
            this.renderCharts();
        },
    });

    core.action_registry.add('game_dashboard', GameDashboard);

    return GameDashboard;
});