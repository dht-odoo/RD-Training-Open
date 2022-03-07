from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "test model6"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')]
    )
    partner_id = fields.Many2one("estate.property.buyer", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        readonly=False
    )
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )

    _sql_constraints = [
        (
            'check_price',
            'CHECK(price > 0 )',
            'Offer Price must be greater than 0'
        ),
    ]

    _order = "price desc"

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.today() + relativedelta(
                days=record.validity
            )

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = record.date_deadline.day - fields.Date.today().day

    def action_confirm(self):
        for record in self:
            record.status = "Accepted"
            record.property_id.state = "Offer Accepted"
            record.property_id.selling_price = self.price
            record.property_id.property_buyer_id = record.partner_id

    def action_refused(self):
        for record in self:
            record.status = "Refused"
