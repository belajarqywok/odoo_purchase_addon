from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError

class autodidak_purchase(models.Model):
    _name = 'autodidak.purchase'

    def get_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/autodidak_purchase/autodidak_purchase_report_excel/%s' % (self.id),
            'target': 'new',
        }

    def func_delete_status_draft(self):
        autodidak_purchase_obj = self.env['autodidak.purchase'].search([('status', '=', 'draft')])
        for line in autodidak_purchase_obj:
            # menghapus record yang memiliki status draft
            line.unlink()
        return True

    def funct_approved(self):
        if self.status == 'draft':
            if self.name == 'New':
                seq = self.env['ir.sequence'].next_by_code('autodidak.purchase') or 'New'
                self.name = seq
            self.status = 'approve'

    def funct_set_to_done(self):
        if self.status == 'approve':
            self.status = 'done'

    @api.model
    def create(self, values):
        res = super(autodidak_purchase, self).create(values)
        for rec in res:
            tanggal_purchase = rec.tanggal
            tanggal_sekarang = date.today()

            if tanggal_purchase < tanggal_sekarang:
                raise ValidationError(_("Tanggal Purchase tidak boleh kurang dari tanggal sekarang"))
            return res

    def write(self, values):
        res = super(autodidak_purchase, self).write(values)
        if 'tanggal' in values:
            tanggal_purchase = self.tanggal
            tanggal_sekarang = date.today()

            if tanggal_purchase < tanggal_sekarang:
                raise ValidationError(_("Tanggal Purchase tidak boleh kurang dari tanggal sekarang"))
        return res

    name = fields.Char(string='Name', default="New")
    tanggal = fields.Date(string='Tanggal')
    status = fields.Selection([
        ('draft','Draft'),
        ('approve','Approve'),
        ('done','Done')
    ], default='draft')
    autodidak_purchase_ids = fields.One2many('autodidak.purchase.line', 'autodidak_purchase_id', string='Autodidak Purchase Ids')
    brand_ids = fields.Many2many('autodidak.brand', 'autodidak_purchase_brand_rel', 'autodidak_purchase_id', 'brand_id', string='Brand Ids')

class autodidak_purchase_line(models.Model):
    _name = 'autodidak.purchase.line'

    @api.onchange('product_id')
    def funct_onchange_product_id(self):
        if not self.product_id:
            return {}
        else:
            self.description = 'Desc - '+ self.product_id.name
        return {}

    def _funct_subtotal(self):
        for line in self:
            line.subtotal = line.price * line.quantity

    autodidak_purchase_id = fields.Many2one('autodidak.purchase', string='Autodidk Purchase Id')
    product_id = fields.Many2one('product.product', string='Produk Id')
    quantity = fields.Float(string='Quantity', default=0)
    uom_id = fields.Many2one('uom.uom', string='Satuan')
    description = fields.Char(string='Description')
    price = fields.Float(string='Harga', default=0.0)
    subtotal = fields.Float(string='Sub Total', compute=_funct_subtotal)

class autodidak_brand(models.Model):
    _name = 'autodidak.brand'

    name = fields.Char(string='Name')

class autodidak_purchase_report_wizard(models.TransientModel):
    _name = 'autodidak.purchase.report.wizard'

    name = fields.Char(string='Name')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

class product_template(models.Model):
    _inherit = 'product.template'

    product_description = fields.Char(string='Product Description')