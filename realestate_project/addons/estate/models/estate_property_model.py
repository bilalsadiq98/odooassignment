from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperties(models.Model):
    _name = "estate.property"

    _description = "Model for Real-Estate Properties"

    name = fields.Char(string='name')

    description = fields.Text(string='description')

    postcode = fields.Char(string='postcode')

    date_availability = fields.Date('available date', attrs={'13/02/2023': 'readonly'}, copy=False)

    expected_price = fields.Float('Expected price')

    selling_price = fields.Float('Selling price', attrs={'130000': 'readonly'}, copy=False)

    bedrooms = fields.Integer('bedrooms', default=2)

    living_area = fields.Float('living area')

    facades = fields.Integer('facades')

    garage = fields.Boolean('garage')

    garden = fields.Boolean('garden')

    garden_area = fields.Float('garden area')

    user_id = fields.Many2one('res.user','userid')

    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
                                          required=True)

    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'North'
        else:
            self.garden_area = False
            self.garden_orientation = False

    state = fields.Selection([('new', 'New'),
                              ('offer_received', 'Offer Received'),
                              ('offer_accepted', 'Offer Accepted'),
                              ('sold', 'Sold'),
                              ('canceled', 'Canceled')], default='new', readonly=True, copy=False)

    def action_cancel(self):
        # for property in self:
        if self.state != 'draft':
            raise UserError("A sold property cannot be canceled.")

        self.state = 'canceled'

    def action_sold(self):
        # for property in self:
        if self.state != 'draft':
            raise UserError("A canceled property cannot be set as sold.")
        self.state = 'sold'

    title = fields.Char(string='Title')

    property_type_id = fields.Many2one('res.partner', string='Property Type')

    buyer_id = fields.Many2one('res.partner', string='Buyer')

    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)

    tag_ids = fields.Many2many('estate.property.tag', string='Tags', )

    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    total_area = fields.Float(string='Total Area', compute='_compute_total_area', copy=False)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        # for record in self:
        self.total_area = self.living_area + self.garden_area

    best_price = fields.Float(string='Best Price', compute="_best_price")

    @api.depends("offer_ids")
    def _best_price(self):
        for record in self:
            if record.offer_ids.mapped('price'):
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

        # return best_price


    _sql_constraints = [

        ('check_expected_price', 'CHECK(expected_price >= 0) ',
         'Expected Price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0) ',
         'Selling Price must be strictly positive'),
        ('check_offer_ids_price', 'CHECK(offer_ids_price >= 0) ',
         'Offer Price must be strictly positive')
    ]


    @api.constrains('selling_price')
    def _check_selling_price(self):
        # for record in self:
        if not float_is_zero(self.selling_price, precision_digits=2) and self.selling_price < (
                self.expected_price * 0.9):
            raise ValidationError("Selling price cannot be lower than 90% of the expected price.")
