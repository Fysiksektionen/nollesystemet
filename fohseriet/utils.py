

menu_item_info = {
    'index': {
        'name': 'Start',
        'url_name': 'fohseriet:index',
        'align': 'left',
        'user': 'any',
    },
    'hantera-event': {
        'name': 'Hantera event',
        'url_name': 'fohseriet:evenemang:lista',
        'align': 'left',
        'user': 'with-permission',
        'permissions' : {
            'logic': 'any',
            'prems': [
                'edit-event',
            ]
        }
    },
    'hantera-andvandare': {
        'name': 'Hantera andvändare',
        'url_name': 'fohseriet:anvandare:index',
        'align': 'left',
        'user': 'with-permission',
        'permissions' : {
            'logic': 'any',
            'prems': [
                'fohseriet.edit_user_info',
                'fohseriet.edit_user_registrations',
            ]
        }
    },
    'fadderiet': {
        'name': 'Fadderiets hemsida',
        'url_name': 'fadderiet:index',
        'align': 'left',
        'user': 'any',
    },
    'logga-ut': {
        'name': 'Logga ut',
        'url_name': 'fohseriet:logga-ut',
        'align': 'right',
        'user': 'logged-in',
    },

    'logga-in': {
        'name': 'Logga in',
        'url_name': 'fohseriet:logga-in:index',
        'align': 'right',
        'user': 'logged-out',
    },
}
