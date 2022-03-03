from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class TestModel(models.Model):
    _name = "estate.property"
    _description = "test model"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    best_price = fields.Float(compute="_compute_best_price")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    total_area = fields.Float(compute="_compute_total_area")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='Status',
        selection=[
            ('New', 'New'),
            ('Offer Received', 'Offer Received'),
            ('Offer Accepted', 'Offer Accepted'),
            ('Sold', 'Sold'),
            ('Canceled', 'Canceled')
        ],
        default="New",
    )
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="property type"
    )
    property_buyer_id = fields.Many2one(
        "estate.property.buyer",
        string="buyer"
    )
    property_seller_id = fields.Many2one(
        "res.users",
        string="partner",
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id")

    _sql_constraints = [
        (
            'check_expected_price',
            'CHECK(expected_price > 0 )',
            'Expected Price must be greater than 0'
        ),
        (
            'check_selling_price',
            'CHECK(selling_price > 0 )',
            'Selling Price must be greater than 0'
        ),
    ]

    _order = "id desc"

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < 0.9*record.expected_price:
                raise ValidationError(r"selling price should be greater than 90% Expected Price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        max_price = 0
        for record in self:
            for offer in record.offer_ids:
                if offer.price >= max_price:
                    max_price = offer.price
            else:
                self.best_price = max_price

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 7
            self.garden_orientation = 'south'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def action_cancel(self):
        for record in self:
            if record.state != "Sold":
                record.state = "Canceled"
                return True
            return {
                'effect': {
                    'fadeout': 'fast',
                    'message': "Sold Property cannot be Canceled",
                }}

    def action_sold(self):
        for record in self:
            if record.state != "Canceled":
                record.state = "Sold"
                return True
            return {
                'effect': {
                    'fadeout': 'fast',
                    'message': "Canceled Property cannot be Sold",
                }}


class TestModel2(models.Model):
    _name = "estate.property.type"
    _description = "test model2"

    name = fields.Char(required=True)
    property_type_ids = fields.One2many("estate.property", "property_type_id")

    _sql_constraints = [
        (
            'check_name',
            'UNIQUE(name)',
            'Name must be unique'
        ),
    ]

    _order = "name"


class TestModel3(models.Model):
    _name = "estate.property.buyer"
    _description = "test model3"

    name = fields.Char(required=True)


class TestModel4(models.Model):
    _name = "estate.property.seller"
    _description = "test model4"

    name = fields.Char(required=True)


class TestModel5(models.Model):
    _name = "estate.property.tag"
    _description = "test model5"

    name = fields.Char(required=True)

    _sql_constraints = [
        (
            'check_name',
            'UNIQUE(name)',
            'tag already exist'
        ),
    ]

    _order = "name"


class TestModel6(models.Model):
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
