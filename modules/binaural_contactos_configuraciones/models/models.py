# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import validations


class TypeWithholdingsBinauralContactos(models.Model):
    _name = 'type.withholding'
    _description = 'Tipo de retención'
    _order = 'create_date desc'
    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'No puedes agregar retenciones con el mismo nombre')]
    
    name = fields.Char(string="Nombre")
    value = fields.Float(string="Valor")
    state = fields.Boolean(default=True, string="Activo")

    @api.onchange('name')
    def upper_name(self):
        return validations.case_upper(self.name, "name")

    @api.onchange('value')
    def onchange_template_id(self):
        res = {}
        if self.value:
            res = {'warning': {
                'title': ('Advertencia'),
                'message': ('Recuerda usar coma (,) como separador de decimales')
                }
            }
    
        if res:
            return res
        
        
class TypePersonBinauralContactos(models.Model):
    _name = "type.person"
    _description = "Tipo de Persona"

    name = fields.Char(string='Descripción', required=True)
    state = fields.Boolean(default=True, string="Activo")
    
    
class TaxUnitBinaural(models.Model):
    _name = "tax.unit"
    _description = "Unidad Tributaria"

    name = fields.Char(string='Descripción',help='Descripción de la Unidad Tributaria', required=True)
    value = fields.Float(string='Valor', help='Valor de la Unidad Tributaria', required=True)
    status = fields.Boolean(default=True, string="¿Activo?")
    
    
class TarifRetentionBinaural(models.Model):
    _name = "tarif.retention"
    _description = "Tarifas"

    @api.depends('apply_subtracting', 'percentage', 'tax_unit_ids')
    def compute_amount_sustract(self):
        if self.apply_subtracting:
            # formula del sustraendo
            # (BaseImponible * %Base) * % Tarifa - (UT * FACTOR(83.334) * PORCENTAJE DE RETENCION)
            self.amount_sustract = self.tax_unit_ids.value * 83.3334 * self.percentage/100

    @api.onchange('percentage')
    def onchange_percentage(self):
        if self.percentage > 100:
            return {
                'warning': {
                    'title': 'Error en campo porcentaje de tarifa',
                    'message': 'el porcentaje no puede exceder el 100%'
                },
                'value': {
                    'percentage': 0
                }
            }

    name = fields.Char(string='Descripción', required=True)
    percentage = fields.Float(string="Porcentaje de tarifa")
    sustract_money = fields.Float(string='Cantidad a restar al porcentaje de la tarifa')
    amount_sustract = fields.Float(string='Monto Sustraendo', compute=compute_amount_sustract, store=True)
    apply_subtracting = fields.Boolean(default=False, string="Aplica sustraendo")
    acumulative_rate = fields.Boolean(default=False, string="¿Tarifa Acumulada?")
    status = fields.Boolean(default=True, string="¿Activo?")
    tax_unit_ids = fields.Many2one('tax.unit', string="Unidad Tributaria", required=True, domain=[('status', '=', True)])
    acumulative_rate_ids = fields.One2many(comodel_name='acumulative.tarif', inverse_name='tariffs_id', string='Tarifa Acumulada')
    
    
class AcumulativeTarifBinaural(models.Model):
    _name = "acumulative.tarif"
    _description = "Tarifas acumuladas"

    name = fields.Char(string='Descripcion', required=True)
    since = fields.Float(string='Desde', required=True)
    until = fields.Float(string='Hasta', help='Deje en blanco para comparar solo con el valor "desde"')
    percentage = fields.Float(string="Porcentaje de tarifa", required=True)
    sustract_ut = fields.Float(string='Restar UT')
    tariffs_id = fields.Many2one('tarif.retention', string='Tarifa acumulada')
    
    
class PaymentConceptBinaural(models.Model):
    _name = "payment.concept"
    _description = "Concepto de Pago"

    name = fields.Char(string="Descripción", required=True)
    line_payment_concept_ids = fields.One2many('payment.concept.line', 'payment_concept_id', 'Linea concepto de pago')
    status = fields.Boolean(default=True, string="Activo")


class PaymentConceptLine(models.Model):
    _name = "payment.concept.line"
    _description = "Linea de concepto de Pago"
    _rec_name = 'code'

    @api.onchange('percentage_tax_base')
    def onchange_percentage(self):
        if self.percentage_tax_base > 100:
            return {
                'warning': {
                    'title': 'Error en campo porcentaje de base imponible',
                    'message': 'el porcentaje no puede exceder el 100%'
                },
                'value': {
                    'percentage_tax_base': 0
                }
            }

    pay_from = fields.Float(string='Pagos mayores a:')
    type_person_ids = fields.Many2one('type.person', string='Tipo de Persona', required=True, domain=[('state', '=', True)])
    payment_concept_id = fields.Many2one('payment.concept', string='Concepto de Pago asociado', required=True, domain=[('status', '=', True)], ondelete='cascade')
    percentage_tax_base = fields.Float(string='Porcentaje Base Imponible')
    tariffs_ids = fields.Many2one('tarif.retention', string='Tarifa', domain=[('status', '=', True)])
    code = fields.Char(string='Codigo de concepto', required=True)
    
    
class SignatureConfigBinuaral(models.Model):
    _name = "signature.config"
    _description = "Configuracion de firma y correo electronico "
    _rec_name = "email"
    
    email = fields.Char(string='Correo electronico')
    signature = fields.Binary(string='Firma')
    active = fields.Boolean(string='Activo', default=True)