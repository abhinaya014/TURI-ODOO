{
    'name': 'Juegalmi Odoo',
    'version': '1.0',
    'summary': 'Modulo JuegAlmi creado por el grupo ADI (Abhinaya Dios, Diego Mermelada E Ibai Fiesta Churro)',
    'category': 'Custom',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/game_api_views.xml',
    ],
    'installable': True,
    'application': True,
}
