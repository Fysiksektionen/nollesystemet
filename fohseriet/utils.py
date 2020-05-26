

menu_item_info = {
    'index': {
        'name': 'Start',
        'url_name': 'fohseriet:index',
        'align': 'left',
        'user': 'any',
    },
    'hantera-event': {
        'name': 'Hantera event',
        'url_name': 'fohseriet:hantera-event',
        'align': 'left',
        'user': 'with-permission',
        'permissions' : {
            'edit-event',
        }
    },
    'hantera-andvandare': {
        'name': 'Hantera andvändare',
        'url_name': 'fohseriet:hantera-andvandare',
        'align': 'left',
        'user': 'with-permission',
        'permissions' : {
            'edit-users',
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
        'name': 'Logga ut',
        'url_name': 'fohseriet:logga-in:index',
        'align': 'right',
        'user': 'logged-out',
    },
}
