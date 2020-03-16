# -*- coding: utf-8 -*-
{
    'name': "almouggar_pos_cache",
    'summary': """
         Improve odoo pos cache""",
    'description': """
        Allow update of pos cache without rebuilding it each time. The only problem of this process 
        is that the deleted products are not deleted from the cache, so the rebuild of the cache is still necessary at some point
    """,
    'author': "Aïmane HOBALLAH",
    'website': "https://www.almouggar.com",
    'category': 'Point of Sale',
    'version': '12.0.0.1.0',
    'depends': ['pos_cache'],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'demo': [
    ]
}
