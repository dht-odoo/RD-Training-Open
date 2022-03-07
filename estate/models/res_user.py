from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class ResUsers(models.Model):
    _inherit = "res.users"
    property_ids = fields.One2many(
        "estate.property", "property_seller_id",
        string="Properties",
        domain=[("state", "in", ["New", "Offer Received"])]
    )
