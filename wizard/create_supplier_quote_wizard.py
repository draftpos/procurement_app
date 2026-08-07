from odoo import models, fields, api, _

class CreateSupplierQuoteWizard(models.TransientModel):
    _name = 'wizard.create.supplier.quote'
    _description = 'Create Supplier Quote Wizard'

    rfq_id = fields.Many2one('custom.rfq', string='RFQ', required=True)
    available_supplier_ids = fields.Many2many('res.partner', compute='_compute_available_suppliers')
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True, domain="[('id', 'in', available_supplier_ids)]")

    @api.depends('rfq_id')
    def _compute_available_suppliers(self):
        for rec in self:
            rec.available_supplier_ids = rec.rfq_id.supplier_ids.mapped('partner_id')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'custom.rfq':
            rfq = self.env['custom.rfq'].browse(active_id)
            res['rfq_id'] = rfq.id
        return res

    def action_create_quote(self):
        self.ensure_one()
        quote_vals = {
            'vendor_id': self.supplier_id.id,
            'line_ids': []
        }
        for line in self.rfq_id.line_ids:
            quote_vals['line_ids'].append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'name': line.name,
            }))
        quote = self.env['custom.supplier.quote'].create(quote_vals)
        return {
            'name': _('Supplier Quote'),
            'type': 'ir.actions.act_window',
            'res_model': 'custom.supplier.quote',
            'res_id': quote.id,
            'view_mode': 'form',
            'target': 'current',
        }
