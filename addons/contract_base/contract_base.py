#encoding: utf-8

from osv import osv
from osv import fields
from tools.translate import _
import time

VoteValues = [('-1', 'Not Voted'), ('0', 'Very Bad'), ('25', 'Bad'), \
        ('50', 'Normal'), ('75', 'Good'), ('100', 'Very Good') ]
DefaultVoteValue = '50'

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
    _description = '合同分类'

    _columns = {
        'name': fields.char('合同号', size=128, required=True),
        'title': fields.char('合同标题', size=512, required=True),
        'start_date': fields.date('起始日期', required=True),
        'end_date': fields.date('截止日期', required=True),
        'category': fields.many2one('contract.category', '合同分类', required=True),
        'partner1': fields.many2one('res.partner', '甲方', required=True),
        'partner2': fields.many2one('res.partner', '乙方', required=True),
        'notes': fields.text('简介'),
    }

    _sql_constraints = [
        ('name', 'unique(name)', '合同号必须唯一' )
    ]
    _order = 'start_date desc, end_date desc, name asc'

Contract()
