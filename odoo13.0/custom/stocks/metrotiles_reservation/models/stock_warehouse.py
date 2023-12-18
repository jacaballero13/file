from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def get_warehouses(self):
        return self.env['stock.warehouse'].search([])