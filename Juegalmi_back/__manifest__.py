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
    ],
    'assets': {
        'web.assets_backend': [
            'Juegalmi_back/static/src/css/player_kanban.css',
        ],
    },
    'installable': True,
    'application': True,
}