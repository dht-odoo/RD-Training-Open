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

        # number of record per page
        limit = 4

        # filtering : "state" in [sold, cancelled]
        domain = [('state', 'not in', ['Sold', 'Cancelled'])                ]
        properties = http.request.env['estate.property']

        # total number of record
        total_records = properties.sudo().search_count(domain,)

        # createing pager
        pager = http.request.website.pager(url='/estate/properties', total=total_records, page=page, step=limit)

        # offset
        offset = pager['offset']
        properties = properties[offset: offset + limit]

        # data to send in frontend side
        data = {
            "properties": properties.search(domain, limit=limit, offset=offset),
            "pager": pager
        }
        response = http.request.render('estate.properties', data)

        # print("*"*100)
        return response
