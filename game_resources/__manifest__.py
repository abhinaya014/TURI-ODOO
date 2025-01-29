{
    'name': 'Game Resources Management',
    'version': '1.0',
    'summary': 'Manage game resources and player inventory',
    'description': """
        This module allows the management of game resources such as items, weapons, and skins.
        It integrates with Unity for synchronization of data.
    """,
    'author': 'ADI BOSS',
    'category': 'Tools',  # Categoría apropiada para el módulo
    'website': 'https://odooadi.duckdns.org',  # URL del módulo o documentación
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'mail', 
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/resource_views.xml',
        'views/player_match_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
