# -*- coding: utf-8 -*-
# 作者：李维
# 创建时间：2012-01-23


{
    'name': '合同管理基础模块',
    'version': '0.1',
    'category': 'Tools',
    'description': """
    用于合同管理的基础模块。
    写更多的简介....
    """,
    'author': '李维',
    'website': 'http://www.dynastech.com',
    'depends': ['base', 'report_aeroo', 'product', 'board'],
    'init_xml': [],
    'update_xml': [
        'security/contract_security.xml',
        #'security/ir.model.access.csv',
        'contract_data.xml', #这行在开发完成之后放到 init_xml 里
        'contract_view.xml',
        'contract_workflow.xml',
        'contract_sequence.xml',
        'report/contract_report_view.xml',
        'report/contract_report.xml',
    ],
    'demo_xml': [
        "contract_demo.xml"
    ],
    'test':[
        #'test/test_idea.yml'
    ],
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
