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


class account_invoice(models.Model):
    _inherit='account.invoice'
    
    @api.one
    @api.depends('invoice_line.price_undiscount_subtotal')
    def _compute_vemo_fields(self):
        self.amount_undiscount_untaxed = sum(line.price_undiscount_subtotal for line in self.invoice_line)
        
    amount_undiscount_untaxed = fields.Float(string='Subtotal Sin Descuento', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_vemo_fields', track_visibility='always')
            
            
class account_invoice_line(models.Model):
    _inherit='account.invoice.line'
    
    price_undiscount_subtotal = fields.Float(string='Amount Undiscount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_vemo_price')
    
    @api.one
    @api.depends('price_unit', 'discount', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_vemo_price(self):
        price = self.price_unit
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_undiscount_subtotal = taxes['total']
        if self.invoice_id:
            self.price_undiscount_subtotal = self.invoice_id.currency_id.round(self.price_undiscount_subtotal)