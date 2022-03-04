from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
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
        string="salesman",
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
            if record.selling_price < 0.9 * record.expected_price:
                raise ValidationError(r"sp should be greater than 90% Expected Price")

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

    def unlink(self):
        if self.state not in ["New", "Canceled"]:
            raise UserError("Only new and canceled properties can be deleted.")
        return super().unlink()


class TestModel2(models.Model):
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
    color = fields.Integer()

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


class ResUsers(models.Model):
    _inherit = "res.users"
    property_ids = fields.One2many(
        "estate.property", "property_seller_id",
        string="Properties",
        domain=[("state", "in", ["New", "Offer Received"])]
    )
