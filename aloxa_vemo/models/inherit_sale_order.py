# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Solucións Aloxa S.L. <info@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
#===============================================================================
# # REMOTE DEBUG
#import pydevd
# 
# # ...
# 
# # breakpoint
#pydevd.settrace("10.0.3.1")
#===============================================================================
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


'''
Modelo que sobreescribe sale.order (Pedidos, Presupuestos)

'''
class sale_order(models.Model):
    _inherit='sale.order'
    
    @api.one
    @api.depends('order_line.price_undiscount_subtotal')
    def _compute_vemo_fields(self):
        self.amount_undiscount_untaxed = sum(line.price_undiscount_subtotal for line in self.order_line)
        
    amount_undiscount_untaxed = fields.Float(string='Subtotal Sin Descuento', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_vemo_fields', track_visibility='always')
    project_title = fields.Char(string='Título')
    project_desc = fields.Text(string='Descripción', translate=True)
    project_locations = fields.One2many('sale.order.project.locations', 'order_tmpl_id', string='Localizaciones')


class sale_order_line(models.Model):
    _inherit='sale.order.line'
    
    price_undiscount_subtotal = fields.Float(string='Amount Undiscount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_vemo_price')
    
    @api.one
    @api.depends('price_unit', 'discount', 'product_uom_qty',
        'product_id', 'order_id.partner_id', 'order_id.currency_id')
    def _compute_vemo_price(self):
        price = self.price_unit
        taxes = self.tax_id.compute_all(price, self.product_uom_qty, product=self.product_id, partner=self.order_id.partner_id)
        self.price_undiscount_subtotal = taxes['total']
        if self.order_id:
            self.price_undiscount_subtotal = self.order_id.currency_id.round(self.price_undiscount_subtotal)


class sale_order_project_locations(models.Model):
    _name = 'sale.order.project.locations'
    _description="Project locations for sale orders"

    location = fields.Char('Ubicación')
    date = fields.Date('Fecha')
    order_tmpl_id = fields.Many2one('sale.order', 'Sale Order')
