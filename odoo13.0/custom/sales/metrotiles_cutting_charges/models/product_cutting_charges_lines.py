# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductCuttingChargesLines(models.Model):
    _name = 'product.cutting.charges.lines'
    _description = "Details of Cutting Charges"

    
    
    @api.depends('is_select', 'contract_qty', 'quantity', 'raw_cut_length')
    def compute_cutting_charge(self):
        total_finished_qty = 0
        amount = 0.00
        has_cutting_multiplier = 0
        cutting_charges_by_lenght = 0
        for line in self:
            has_cutting_multiplier = (line.quantity * (float(line.contract_qty)))
            total_cutting_charges = (has_cutting_multiplier) * float(line.cut_length)
            cutting_charges_by_lenght += total_cutting_charges
            if line.is_select:
                if line.contract_qty <= 0:
                    raise UserError('Contract Quantity must not be less than to Zero')
                else:
                    if float(line.raw_cut_width) % float(line.cut_width) == 0 and float(line.raw_cut_length) % float(line.cut_length) == 0:
                        line.update({'cutting_charges': cutting_charges_by_lenght })
                    else:
                        cutting_excess = float(line.cut_width) + float(line.cut_length)
                        cutting_total = cutting_excess * (float(line.contract_qty))
                        line.update({'cutting_charges': cutting_total })
            else:
                line.update({'cutting_charges':  amount})
        
        return line

    @api.depends('per_sqm', 'quantity')
    def compute_finished_qty(self):
        for record in self:
            record.update({'finished_qty': (record.per_sqm * record.quantity) })
        return record
    
    @api.depends('raw_cut_width', 'raw_cut_length', 'cut_width', 'cut_length')
    def compute_per_sqm(self):
        for line in self:
            cutting_size =  (float(line.raw_cut_width or 1) / float(line.cut_width or 1)) * \
                            (float(line.raw_cut_length or 1) / float(line.cut_length or 1))
            line.update({'per_sqm': cutting_size })
        return line

    @api.depends('bom')
    def get_raw_cut_size(self):
        for rec in self:
            raw_cut_size = "00x00"
            raw_cut_width = ""
            raw_cut_length = ""
            for om in rec.bom:
                for bom_ids in om.bom_line_ids:
                    for attr in bom_ids.product_id.product_template_attribute_value_ids:
                        if attr.attribute_id.name == 'Sizes':
                            raw_cut_size = attr.name
                        if rec.bom:
                            rcut_size = raw_cut_size.split("x")
                            raw_cut_width = rcut_size[0]
                            raw_cut_length = rcut_size[1]
            rec.update({'raw_cut_width': raw_cut_width, 
                        'raw_cut_length': raw_cut_length 
                    })
    def _inverse_raw_cut_size(self):
        for rec in self:
            raw_cut_size = "00x00"
            raw_cut_width = ""
            raw_cut_length = ""
            for om in rec.bom:
                for bom_ids in om.bom_line_ids:
                    for attr in bom_ids.product_id.product_template_attribute_value_ids:
                        if attr.attribute_id.name == 'Sizes':
                            raw_cut_size = attr.name
                        if rec.bom:
                            rcut_size = raw_cut_size.split("x")
                            raw_cut_width = rcut_size[0]
                            raw_cut_length = rcut_size[1]
            rec.update({'raw_cut_width': raw_cut_width, 
                        'raw_cut_length': raw_cut_length 
                    })
        
    @api.depends('product_id')
    def get_cut_size(self):
        for rec in self:
            mraw_cut_size = "00x00"
            cut_width = ""
            cut_length = ""
            for attr in rec.product_id.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Sizes':
                    mraw_cut_size = attr.name
                if rec.product_id:
                    cut_size = mraw_cut_size.split("x")
                    cut_width = cut_size[0]
                    cut_length = cut_size[1]
            rec.update({'cut_width': cut_width, 
                        'cut_length': cut_length
                    })

    # @api.depends('product_id')
    # def get_description(self):
    #     for rec in self:
    #         for product in rec.product_id:
    #             if rec.product_id:
    #                 rec.description = product.name
                    
    #         return rec

    # def _inverse_product(self):
    #     for rec in self:
    #         for product in rec.product_id:
    #             if rec.product_id:
    #                 rec.description = product.name
                    
    #         return rec

    
    cutting_charge_sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Cutting Charge",
    )
    
    product_id = fields.Many2one(comodel_name='product.product', string="Description", store=True)

    location_id = fields.Many2one(comodel_name='metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one(comodel_name='metrotiles.application', string="Application", store=True)

    factory_id = fields.Many2one(comodel_name='res.partner', string='Factory',store=True)
    series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False,store=True)
    # description = fields.Char('Description', compute="get_description")
    variant = fields.Char(string="Variant")
    bom = fields.Many2one(
        comodel_name='mrp.bom',
        string="Raw Material",
        store=True,
    )
    quantity = fields.Float(
        string="Quantity",
    )
    # raw meterial to be cut
    raw_cut_width = fields.Float(
        string='Cut Width',
        compute="get_raw_cut_size",
        inverse='_inverse_raw_cut_size',
        store=True,
    )
    raw_cut_length = fields.Float(
        string="Cut Length",
        compute="get_raw_cut_size",
        inverse='_inverse_raw_cut_size',
        store=True,
    )
    cut_width = fields.Float(
        string="Width",
        compute='get_cut_size',
        inverse='_inverse_raw_cut_size',
        store=True,
    )    
    cut_length = fields.Float(
        string="Length",
        compute='get_cut_size',
        inverse='_inverse_raw_cut_size',
        store=True,
    )
    per_sqm = fields.Float(
        string="(PC)Per-SQM",
        readonly=True,
        compute="compute_per_sqm",
    )
    finished_qty = fields.Float(
        string="Finished Qty",
        compute="compute_finished_qty",
        store=True,
    )
    contract_qty = fields.Float(
        string="Contract Qty",
        store=True,
    )
    cutting_charges = fields.Float(
        string="Charges SubTotal",
        compute="compute_cutting_charge",
        store=True,
    )
    is_select = fields.Boolean(
        string="Select",
    )
    excess = fields.Float(
        string="Excess",
        default=0.0,
    )
    to_fabricate = fields.Boolean(
        string="Fabricated",
        store = True,
    )

    
    
    