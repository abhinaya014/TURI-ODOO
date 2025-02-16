{
    'name': 'Juegalmi Odoo',
    'version': '1.0',
    'summary': 'Modulo JuegAlmi creado por el grupo ADI (Abhinaya Dios, Diego Mermelada E Ibai Fiesta Churro)',
    'category': 'Custom',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/player.xml',
        'views/skin.xml',
        'views/match.xml',
        'views/menu.xml',
        'views/transic.xml',
        'views/achievement_views.xml',
        'views/dashboard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'Juegalmi_back/static/src/css/player_kanban.css',
            'Juegalmi_back/static/src/js/dashboard.js',
            'Juegalmi_back/static/src/css/dashboard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js',


        ],
    },
    'installable': True,
    'application': True,
}