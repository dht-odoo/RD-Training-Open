from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class EstatePropertySeller(models.Model):
    _name = "estate.property.seller"
    _description = "test model4"

    name = fields.Char(required=True)
