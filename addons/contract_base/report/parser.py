#encoding: utf-8
##############################################################################
#
#    A Chinese Business Contract Management Module for OpenERP
#    Copyright (C) 2012-2014 Sandwych Consulting LLC (<http://www.sandwych.com>)
#    Author: Wei "oldrev" Li <liwei@sandwych.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64

from osv import osv,fields
from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):

    def get_template(self, cursor, user):
        return self.report_data

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'hello_world':self.hello_world,
        })
        ids = [context['active_id']]
        self.record_id = context['active_id']
        contract_rec = self.pool.get('contract.contract').browse(cr, uid, ids, context=context)[0]
        base64_data = contract_rec.category.report_template
        if base64_data:
            self.report_data = base64.decodestring(base64_data)
        else:
            self.report_data = False

    def hello_world(self, name):
        return "Hello, %s!" % name


