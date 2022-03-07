from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "test model2"

    name = fields.Char(required=True)
    property_type_ids = fields.One2many("estate.property", "property_type_id")
    Sequence = fields.Integer()
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer")
    offer_ids = fields.One2many("estate.property.offer", string="Offers", compute="_compute_offer")

    _sql_constraints = [
        (
            'check_name',
            'UNIQUE(name)',
            'Name must be unique'
        ),
    ]

    _order = "name"

    def action_count_offer(self):
        pass

    def _compute_offer(self):
        # will have to check once again
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])
