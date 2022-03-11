# -*- coding: utf-8 -*-
from odoo import http


class Estate(http.Controller):
    @http.route('/estate', auth='public', website=True)
    def index(self):
        return http.request.render('estate.index')

    @http.route(['/estate/properties', '/estate/properties/page/<int:page>'], auth='public', website=True)
    def property_view(self, page=1, **kwarg):

        # number of record per page
        limit = 4

        # filtering : "state" in [sold, cancelled]
        domain = [('state', 'not in', ['Sold', 'Cancelled'])                ]
        properties = http.request.env['estate.property']

        # applying filteration based on date, if available
        date = kwarg.get('date')
        if date:
            domain.append(('create_date', '>=', date))

        # filtering : if user is admin or not
        if http.request.env.user.has_group('base.group_portal'):
            domain.append(('is_published', '=', 'True'))

        # total number of record
        total_records = properties.sudo().search_count(domain,)

        # createing pager
        pager = http.request.website.pager(url='/estate/properties', total=total_records, page=page, step=limit)

        # offset
        offset = pager['offset']
        properties = properties[offset: offset + limit]

        # data to send in frontend side
        data = {
            "properties": properties.search(domain, limit=limit, offset=offset, order="create_date desc"),
            "pager": pager
        }
        response = http.request.render('estate.properties', data)

        # print("*"*100)
        return response

    @http.route('/estate/property/<model("estate.property"):name>', auth='public', website=True)
    def property_view_form(self, name):
        data = {
            "property": name
        }
        response = http.request.render('estate.object', data)
        return response
