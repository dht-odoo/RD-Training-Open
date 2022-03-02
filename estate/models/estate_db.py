from odoo import fields, models, api
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
        string='Type',
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

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            for offers in record.offer_ids:
                record.best_price = max(record.offer_ids)


class TestModel2(models.Model):
    _name = "estate.property.type"
    _description = "test model2"

    name = fields.Char(required=True)


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


class TestModel6(models.Model):
    _name = "estate.property.offer"
    _description = "test model6"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')]
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
