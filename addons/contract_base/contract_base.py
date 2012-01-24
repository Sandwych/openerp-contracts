#encoding: utf-8

from osv import osv
from osv import fields
from tools.translate import _
import time


class ContractGroup(osv.osv):
    """ 合同分组 """
    _name = 'contract.group'
    _description = '合同分组'
    _columns = {
        'name': fields.char('分组名称', size=256, required=True),
        'start_date': fields.date('起始日期', required=True),
        'end_date': fields.date('截止日期', required=True),
        'notes': fields.text('简介'),
        'contracts': fields.one2many('contract.contract', 'group', '合同'),# readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', '合同组所属机构', required=False),
    }
    _sql_constraints = [
        ('name', 'unique(name)', '分组名称必须唯一' )
    ]
    _order = 'start_date desc, end_date desc, name asc'
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'contract.group', context=c),
    }

ContractGroup()


class Category(osv.osv):
    """ 合同分类 """
    _name = 'contract.category'
    _description = '合同分类'
    _columns = {
        'name': fields.char('分类名称', size=64, required=True),
        'summary': fields.text('简介'),
        'parent_id': fields.many2one('contract.category', '上级分类', ondelete='set null'),
        'child_ids': fields.one2many('contract.category', 'parent_id', '下级分类'),
    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', '分类名称必须唯一' )
    ]
    _order = 'parent_id,name asc'

Category()


class Contract(osv.osv):
    """ 合同文书 """
    _name = 'contract.contract'
    _description = '合同文书'
    _columns = {
        'name': fields.char('合同号', size=128, required=True),
        'title': fields.char('合同标题', size=512, required=True),
        'group': fields.many2one('contract.group', '所属分组', required=False, ondelete='set null'),
        'start_date': fields.date('起始日期', required=True),
        'end_date': fields.date('截止日期', required=True),
        'category': fields.many2one('contract.category', '合同分类', required=True),
        'partner1': fields.many2one('res.partner', '甲方', required=True),
        'partner2': fields.many2one('res.partner', '乙方', required=True),
        'notes': fields.text('简介'),
        'lines': fields.one2many('contract.contract.line', 'contract_id', '标的物收付计划'),# readonly=True, states={'draft': [('readonly', False)]}),
        'fund_lines': fields.one2many('contract.contract.fund_line', 'contract_id', '资金计划'),# readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.related('group', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True)
    }
    _sql_constraints = [
        ('name', 'unique(name)', '合同号必须唯一' )
    ]
    _order = 'start_date desc, end_date desc, name asc'

Contract()


class ContractLine(osv.osv):
    """ 标的物收付计划 """
    _name = 'contract.contract.line'
    _description = '标的物收付计划'
    _columns = {
        'contract_id': fields.many2one('contract.contract', '合同引用', required=True, ondelete='cascade', select=True),
        'name': fields.char('说明', size=256, required=True, select=True),
        'sequence': fields.integer('序号', help='序号，用于指定该记录在列表中显示的顺序，数字越小越靠前，不要求连续'),
        'product': fields.many2one('product.product', '产品'),
        'uom': fields.many2one('product.uom', '计量单位', required=True),
        'quantity': fields.float('数量（按单位计）', digits=(16, 2), required=True),
        'planned_date': fields.date('计划收付日期', required=True),
        'notes': fields.text('备注'),
        'company_id': fields.related('contract_id', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True)
    }
    _order = 'sequence asc, id desc'

ContractLine()


class ContractFundLine(osv.osv):
    """ 标的物收付计划 """
    _name = 'contract.contract.fund_line'
    _description = '收付款计划'
    _columns = {
        'contract_id': fields.many2one('contract.contract', '合同引用', required=True, ondelete='cascade', select=True),
        'name': fields.char('说明', size=256, required=True, select=True),
        'sequence': fields.integer('序号', help='序号，用于指定该记录在列表中显示的顺序，数字越小越靠前，不要求连续'),
        'planned_date': fields.date('计划收付日期', required=True),
        'type': fields.char('结算方式', size=256, required=True, select=True),
        'payterm': fields.char('资金条款', size=256, required=True, select=True),
        'amount': fields.float('金额', required=True),
        'notes': fields.text('备注'),
        'company_id': fields.related('contract_id', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True)
    }
    _order = 'sequence asc, id desc'

ContractFundLine()

