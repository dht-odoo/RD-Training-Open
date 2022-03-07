from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "test model5"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        (
            'check_name',
            'UNIQUE(name)',
            'tag already exist'
        ),
    ]

    _order = "name"
