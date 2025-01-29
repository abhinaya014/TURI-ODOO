from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GameResource(models.Model):
    _name = 'game.resource'
    _description = 'Game Resource'
    _order = 'name'

    name = fields.Char(string='Resource Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    category = fields.Selection([
        ('weapon', 'Weapon'),
        ('skin', 'Skin'),
        ('ability', 'Ability'),
    ], string='Category', required=True)
    availability = fields.Boolean(string='Available', default=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=lambda self: self.env.company.currency_id.id)
    image = fields.Binary(string='Image', attachment=True)

    def toggle_availability(self):
        for record in self:
            record.availability = not record.availability