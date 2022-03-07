from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyBuyer(models.Model):
    _name = "estate.property.buyer"
    _description = "test model3"

    name = fields.Char(required=True)
