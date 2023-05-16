from odoo import models, fields, api
from odoo.exceptions import UserError
# from datetime import datetime, timedelta
# from datetime import date
import datetime

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

    price = fields.Float(string='Price')
    accepted = fields.Boolean(string='Accepted', default=False)
    refused = fields.Boolean(string='Refused', default=False)
    selling_price = fields.Float(string='Selling Price')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    validity_days = fields.Integer(default=7)
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        string='Status',
        default=False,
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    property_id = fields.Many2one(
        'estate.property',
        string='Property',
        required=True,
    )

    validity = fields.Integer(string='Validity', default=7)
    date_deadline = fields.Date(string='Deadline', compute='_date_deadline', inverse='_inverse_date_deadline')
    create_date = fields.Date()

    @api.depends("create_date", "validity_days")
    def _date_deadline(self):
        for record in self:
            record.create_date = datetime.date.today()
            record.date_deadline = fields.Date.add(record.create_date, days=+record.validity_days)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity_days
            record.validity_days = (record.date_deadline - datetime.date.today()).days

        _accepted = fields.Boolean(string='Accepted', default=False)
        _refused = fields.Boolean(string='Refused', default=False)

    def action_accept(self):
        self.ensure_one()
        self.accepted = True
        self.refused = False

        if self.property_id:
            previous_accepted_offer = self.property_id.offers.filtered(lambda o: o.accepted)
            if previous_accepted_offer:
                previous_accepted_offer.write({'accepted': False})

            self.buyer_id = self.buyer_id
            self.selling_price = self.price

    def action_refuse(self):
        self.ensure_one()
        self.accepted = False
        self.refused = True



