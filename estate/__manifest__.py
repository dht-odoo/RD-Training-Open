{
    'name': "Real Estate",
    'depends': [
        'base',
    ],
    'data': [
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
    ],
    'application': True,
    'installable': True,
}
