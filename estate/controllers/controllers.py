# -*- coding: utf-8 -*-
from odoo import http


class Estate(http.Controller):
    @http.route('/estate', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('estate.index')

    @http.route('/estate/properties', auth='public', website=True)
    def property_view(self, **kwargs):

        # getting page number if available
        page = kwargs.get('page', 1)
        

        # filtering : "state" in [sold, cancelled]
        domain = [('state', 'not in', ['Sold', 'Cancelled'])                ]
        properties = http.request.env['estate.property']
        # print("*"*100)

        # data to send in frontend side
        data = {
            "properties": properties.search( domain, limit=4 )
        }
        response = http.request.render('estate.properties', data)
        return response
