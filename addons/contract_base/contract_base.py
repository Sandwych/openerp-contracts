#encoding: utf-8

from osv import osv
from osv import fields
from tools.translate import _
import time
from datetime import datetime


class ContractGroup(osv.osv):
    """ 合同分组 """
    _name = 'contract.group'
    _description = 'Contract Group'

    def _total_amount(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0.0
            for c in o.contracts:
                total_amount = total_amount + c.total_amount
            result[o.id] = total_amount
        return result

    def _paid_amount(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0.0
            for c in o.contracts:
                total_amount = total_amount + c.paid_amount
            result[o.id] = total_amount
        return result

    def _paid_rate(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0.0
            paid_amount = 0.0
            for c in o.contracts:
                total_amount = total_amount + c.total_amount
                paid_amount = paid_amount + c.paid_amount
            if paid_amount < 0.0001:
                result[o.id] = 0.0
            else:
                result[o.id] = round(100.0 * paid_amount / total_amount, 2)
        return result

    _columns = {
        'name': fields.char('分组名称', size=256, required=True),
        'start_date': fields.date('起始日期', required=True),
        'end_date': fields.date('截止日期', required=True),
        'note': fields.text('简介'),
        'contracts': fields.one2many('contract.contract', 'group', '合同'),# readonly=True, states={'draft': [('readonly', False)]}),
        'total_amount': fields.function(_total_amount, method=True, string='计划收付', type='float'),
        'paid_amount': fields.function(_paid_amount, method=True, string='已收付', type='float'),
        'paid_rate': fields.function(_paid_rate, method=True, string='资金进度', type='float'),
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
    _description = 'Contract Category'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('分类名称', size=64, required=True, translate=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='分类名称'),
        'parent_id': fields.many2one('contract.category','上级分类 ', select=True, ondelete='cascade'),
        'children': fields.one2many('contract.category', 'parent_id', string='下级分类'),
        'sequence': fields.integer('序号', select=True, help="用于决定该分类的排序，数字越小显示越靠前"),
        'type': fields.selection([('view','视图'), ('normal','普通')], '分类类型 '),
        'fund_type': fields.selection([('out', '付款'), ('in', '收款')], '资金性质', required=False),
        'report_template': fields.binary('合同文档模板', required=False, \
            help="如果一个合同指定了属于此分类，那么将使用此模板文件打印合同文档。此模板应使用 .ODT 格式。"),
        'summary': fields.text('简介'),
        #下面两个是系统内部使用的字段
        'parent_left': fields.integer('Left Parent', required=True),
        'parent_right': fields.integer('Right Parent', required=True),
    }
    _sql_constraints = [
        ('name', 'unique(name)', '分类名称必须唯一' )
    ]
    _defaults = {
        'type' : lambda *a : 'normal',
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'
    
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id FROM contract_category WHERE "id" IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive categories.', ['parent_id'])
    ]

    def child_get(self, cr, uid, ids):
        return [ids]

Category()


class Contract(osv.osv):
    """ 合同文书 """
    _name = 'contract.contract'
    _description = 'Contract Information'

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, ['|',('code',operator,name),('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['code', 'name'], context, load='_classic_write')
        return [(x['id'], ('[' + x['code'] + '] ' + x['name'])) for x in reads]

    def _total_amount(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0
            for l in o.fund_lines:
                total_amount = total_amount + l.amount
            result[o.id] = total_amount
        return result

    def _paid_amount(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0.0
            for fl in o.fund_lines:
                total_amount = total_amount + fl.paid_amount
            result[o.id] = total_amount
        return result

    def _paid_rate(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            total_amount = 0.0
            paid_amount = 0.0
            for fl in o.fund_lines:
                total_amount = total_amount + fl.amount
                paid_amount = paid_amount + fl.paid_amount
            if paid_amount < 0.0001:
                result[o.id] = 0.0
            else:
                result[o.id] = round(100.0 * paid_amount / total_amount, 2)
        return result


    def _get_default_partner(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.partner_id.id


    _columns = {
        'code': fields.char('合同号', size=128, required=True),
        'name': fields.char('合同主题', size=512, required=True),
        'group': fields.many2one('contract.group', '所属分组', required=False, ondelete='set null'),
        'sign_date': fields.date('订立日期', required=True),
        'start_date': fields.date('起始日期', required=True),
        'end_date': fields.date('截止日期', required=True),
        'category': fields.many2one('contract.category', '合同分类', required=True),
        'fund_type': fields.related('category', 'fund_type', type='selection', string='资金性质', store=True, readonly=True),
        'partner1': fields.many2one('res.partner', '甲方', required=True),
        'partner2': fields.many2one('res.partner', '乙方', required=True),
        'note': fields.text('简介'),
        'lines': fields.one2many('contract.contract.line', 'contract_id', '标的物收付计划'),# readonly=True, states={'draft': [('readonly', False)]}),
        'fund_lines': fields.one2many('contract.contract.fund_line', 'contract_id', '资金计划'),# readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.related('group', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True),
        'total_amount': fields.function(_total_amount, method=True, string='计划收付', type='float'),
        'paid_amount': fields.function(_paid_amount, method=True, string='已收付', type='float'),
        'paid_rate': fields.function(_paid_rate, method=True, string='资金进度', type='float'),
        'user_id': fields.many2one('res.users', '负责人', required=False),
        'state': fields.selection([
                ('draft', '草稿'),
                ('confirmed', '已审核'),
                ('done', '完成'),
                ('abort', '终止'),
                ('cancel', '取消')
                ], '合同状态', readonly=True, select=True),
    }
    _sql_constraints = [
        ('name', 'unique(name)', '合同号必须唯一' )
    ]
    _order = 'start_date desc, end_date desc, name asc'
    _defaults = {
        'sign_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'partner1': _get_default_partner,
    }

Contract()


class ContractLine(osv.osv):
    """ 标的物收付计划 """
    _name = 'contract.contract.line'
    _description = 'Contract Detail'
    _columns = {
        'contract_id': fields.many2one('contract.contract', '合同引用', required=True, ondelete='cascade', select=True),
        'name': fields.char('说明', size=256, required=True, select=True),
        'product': fields.many2one('product.product', '产品'),
        'uom': fields.many2one('product.uom', '计量单位', required=True),
        'quantity': fields.float('数量（按单位计）', digits=(16, 2), required=True),
        'unit_price': fields.float('单价', required=True, digits=(16, 2)), #, readonly=True, states={'draft': [('readonly', False)]}),
        'planned_date': fields.date('计划收付日期', required=True),
        'note': fields.text('备注'),
        'company_id': fields.related('contract_id', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True)
    }
    _order = 'planned_date asc, id desc'

    def onchange_product(self, cr, uid, ids, product_id, quantity):
        v = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            v['uom'] = product.uom_id.id
            v['unit_price'] = product.list_price
            v['name'] = product.name
        return {'value':v}

ContractLine()


class ContractFundLine(osv.osv):
    """ 款项收付计划 """
    _name = 'contract.contract.fund_line'
    _description = 'Contract Fund Line'

    def _paid_amount(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        sql = '''
        SELECT l.id, SUM(p.amount)
            FROM contract_contract_fund_line l
            LEFT JOIN contract_contract_fund_payment p ON p.fund_line = l.id
            WHERE l.id IN %s GROUP BY l.id
        '''
        cursor.execute(sql, (tuple(ids),))
        for lineid, amount_sum in cursor.fetchall():
            result[lineid] = amount_sum
        return result

    def _paid_rate(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            paid_amount = o.paid_amount
            if paid_amount < 0.0001:
                result[o.id] = 0.0
            else:
                result[o.id] = round(100.0 * o.paid_amount / o.amount, 2)
        return result

    _columns = {
        'contract_id': fields.many2one('contract.contract', '合同引用', required=True, ondelete='cascade', select=True),
        'name': fields.char('说明', size=256, required=True, select=True),
        'planned_date': fields.date('计划收付日期', required=True),
        'type': fields.char('结算方式', size=256, required=True, select=True),
        'payment_term': fields.char('资金条款', size=256, required=False),
        'amount': fields.float('金额', required=True),
        'paid_amount': fields.function(_paid_amount, method=True, string='已收付金额', type='float'),
        'paid_rate': fields.function(_paid_rate, method=True, string='已收付比率', type='float'),
        'note': fields.text('备注'),
        'user_id': fields.many2one('res.users', '负责人', required=False),
        'company_id': fields.related('contract_id', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True)
    }
    _order = 'planned_date asc, id desc'
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }

ContractFundLine()


class ContractFundPayment(osv.osv):
    """ 款项收付记录 """
    _name = 'contract.contract.fund_payment'
    _description = 'Contract Fund Payment'

    def _get_delayed_days(self, cursor, user, ids, field_name, arg, context=None):
        result = {}
        for o in self.browse(cursor, user, ids, context=context):
            d1 = datetime.strptime(o.pay_date, '%Y-%m-%d')
            d2 = datetime.strptime(o.fund_line.planned_date, '%Y-%m-%d')
            result[o.id] = (d1 - d2).days
        return result

    _columns = {
        'fund_line': fields.many2one('contract.contract.fund_line', '款项收付计划', required=True, ondelete='cascade', select=True),
        'contract': fields.related('fund_line', 'contract_id', type='many2one', relation='contract.contract', string='合同', store=True, readonly=True),
        'name': fields.char('说明', size=256, required=True, select=True),
        'pay_date': fields.date('收付款日期', required=True),
        'planned_date': fields.related('fund_line', 'planned_date', type='date', string='合同计划日期', store=True, readonly=True),
        'amount': fields.float('金额', required=True),
        'delayed_days': fields.function(_get_delayed_days, method=True, string='延迟天数', type='integer'),
        'note': fields.text('备注'),
        'user_id': fields.many2one('res.users', '负责人', required=False),
        'company_id': fields.related('fund_line', 'company_id', type='many2one', relation='res.company', string='所属机构', store=True, readonly=True),
    }
    _order = 'pay_date desc, id desc'
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'pay_date': lambda *a: time.strftime('%Y-%m-%d'),
    }

ContractFundPayment()
