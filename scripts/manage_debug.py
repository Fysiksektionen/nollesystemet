#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import scripts.manage as manage_prod


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_administration.settings.development')
    manage_prod.main()


if __name__ == '__main__':
    main()
