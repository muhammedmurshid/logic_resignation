{
    'name': "Logic Resignation",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['mail', 'base', 'hr_resignation', 'leads'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/resignation.xml',
        'data/activity.xml'

    ],
    'demo': [],
    'summary': "logic_resignation",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}
