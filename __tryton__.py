# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Calendar Classification',
    'name_de_DE' : 'Kalender Klassifikation',
    'name_es_CO' : 'Clasificación del calendario',
    'name_es_ES' : 'Clasificación del calendario',
    'name_fr_FR' : 'Classification calendrier',
    'version' : '1.6.0',
    'author' : 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': 'Handle classification of event',
    'description_de_DE' : '''
    Fügt Unterstützung für die Klassifikation von Terminen in CalDAV hinzu.
''',
    'description_es_CO': 'Gestiona la clasificación de eventos en CalDAV',
    'description_es_ES': 'Gestiona la clasificación de eventos en CalDAV',
    'description_fr_FR': 'Gère la classification des évènements',
    'depends' : [
        'ir',
        'calendar',
    ],
    'xml' : [
    ],
    'translation': [
        'de_DE.csv',
        'es_CO.csv',
        'es_ES.csv',
        'fr_FR.csv',
    ],
}
