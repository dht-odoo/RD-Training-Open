from odoo import models, fields, api


class TagWizard(models.TransientModel):
    _name = "tag.wizard"
    _description = "to add tag"

    tag_id = fields.Many2many('estate.property.tag')

    def action_add_tag(self):
        self.ensure_one()
        activeIds = self.env.context.get('active_ids')
        for x in activeIds:
            a = self.env['estate.property'].browse(x)
            self.env['estate.property'].browse(x).write({'tag_ids': a.tag_ids + self.tag_id})
        return True
