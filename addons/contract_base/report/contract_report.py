# -*- coding: utf-8 -*-

from osv import fields,osv
import tools

class ContractFundReport(osv.osv):
    _name = 'report.contract.fund_by_category'
    _description = 'Contract Fund Report'
    _auto = False
    _columns = {
        'name': fields.char('分类名称', size=128, readonly=True),
        'year': fields.char('年', size=16, readonly=True),
        'month': fields.char('月', size=16, readonly=True),
        'day': fields.char('日', size=16, readonly=True),
        'days': fields.integer('天数', readonly=True),
        'start_date': fields.date('起始日期', readonly=True),
        'end_date': fields.date('截止日期', readonly=True),
        'sign_date': fields.date('签订日期', readonly=True),
        'partner2': fields.many2one('res.partner', '乙方', readonly=True),
        'amount': fields.float('总金额', readonly=True),
        'paid_amount': fields.float('已收付金额', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True, groups="base.group_multi_company"),
    }
    _order = 'name desc, sign_date asc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_contract_fund_by_category')
        cr.execute('''
            CREATE VIEW report_contract_fund_by_category AS
            SELECT
                MIN(c.id) "id", 
                cat.name "name", 
                SUM(fl.amount) "amount", 
                SUM(fl.paid_amount) "paid_amount", 
                TO_CHAR(c.start_date, 'YYYY') "year",
                TO_CHAR(c.start_date, 'MM') "month",
                TO_CHAR(c.start_date, 'YYYY-MM-DD') "day",
                DATE_TRUNC('day', c.start_date) "start_date",
                DATE_TRUNC('day', c.end_date) "end_date",
                DATE_TRUNC('day', c.sign_date) "sign_date",
                ABS((EXTRACT(EPOCH FROM (c.end_date::TIMESTAMP - c.start_date::TIMESTAMP))) / (3600 * 24)) "days",
                c.partner2 partner2,
                c.company_id company_id
            FROM contract_contract c
            LEFT JOIN contract_contract_fund_line fl ON fl.contract_id = c.id
            INNER JOIN contract_category cat ON cat.id = c.category
            GROUP BY c.id, cat.name, c.start_date, c.end_date, c.sign_date, c.partner2, c.company_id

        ''')

ContractFundReport()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

