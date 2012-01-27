#encoding: utf-8

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


