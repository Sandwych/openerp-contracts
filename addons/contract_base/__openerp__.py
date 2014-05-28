# -*- coding: utf-8 -*-
# 作者：李维
# 创建时间：2012-01-23
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


{
    'name': '合同管理基础模块',
    'version': '0.1',
    'category': 'Tools',
    'description': """
    用于合同管理的基础模块。
    写更多的简介....
    """,
    'author': '李维',
    'website': 'http://www.sandwych.com',
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
