from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"

    _description = "Model for Real-Estate Properties Tag"

    name = fields.Char(required=True)


_sql_constraints = [
    ('unique_property_tag_name', 'UNIQUE(name)', 'Property tag name must be unique.'),
]
