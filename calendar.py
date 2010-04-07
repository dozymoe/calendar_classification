#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL
from trytond.tools import reduce_ids
import vobject


class Event(ModelSQL):
    _name = 'calendar.event'

    def __init__(self):
        super(Event, self).__init__()
        self._error_messages.update({
            'transparent': 'Free',
            'opaque': 'Busy',
            })

    def search(self, cursor, user, domain, offset=0, limit=None, order=None,
            context=None, count=False, query_string=False):
        if user:
            domain = domain[:]
            domain = [domain,
                    ['OR',
                        [
                            ('classification', '=', 'confidential'),
                            ['OR',
                                ('calendar.owner', '=', user),
                                ('calendar.write_users', '=', user),
                            ],
                        ],
                        ('classification', '!=', 'confidential'),
                    ]]
        return super(Event, self).search(cursor, user, domain, offset=offset,
                limit=limit, order=order, context=context, count=count,
                query_string=query_string)

    def create(self, cursor, user, values, context=None):
        new_id = super(Event, self).create(cursor, user, values, context=context)
        if self.search(cursor, user,
                [('id', '=', new_id)], context=context, count=True) != 1:
            self.raise_user_error(cursor, 'access_error',
                    self._description, context=context)
        return new_id

    def _clean_private(self, cursor, user, record, transp, context=None):
        '''
        Clean private record

        :param cursor: the database cursor
        :param user: the user id
        :param record: a dictionary with record values
        :param transp: the time transparency
        :param context: the context
        '''
        summary = self.raise_user_error(cursor, transp, raise_exception=False,
                context=context)
        if 'summary' in record:
            record['summary'] = summary

        vevent = None
        if 'vevent' in record:
            vevent = record['vevent']
            if vevent:
                vevent = vobject.readOne(vevent)
                if hasattr(vevent, 'summary'):
                    vevent.summary.value = summary

        for field, value in (
                ('description', ''),
                ('categories', []),
                ('location', False),
                ('status', ''),
                ('organizer', ''),
                ('attendees', []),
                ('alarms', [])):
            if field in record:
                record[field] = value
            if field + '.rec_name' in record:
                record[field + '.rec_name'] = ''
            if vevent:
                if hasattr(vevent, field):
                    delattr(vevent, field)
        if vevent:
            record['vevent'] = vevent.serialize()

    def read(self, cursor, user, ids, fields_names=None, context=None):
        rule_obj = self.pool.get('ir.rule')
        int_id = False
        if isinstance(ids, (int, long)):
            int_id = True
            ids = [ids]
        if len({}.fromkeys(ids)) != self.search(cursor, user,
                [('id', 'in', ids)], context=context, count=True):
            self.raise_user_error(cursor, 'access_error',
                    self._description, context=context)

        writable_ids = []
        domain1, domain2 = rule_obj.domain_get(cursor, user, self._name,
                mode='write', context=context)
        if domain1:
            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]
                red_sql, red_ids = reduce_ids('id', sub_ids)
                cursor.execute('SELECT id FROM "' + self._table + '" ' \
                        'WHERE ' + red_sql + ' AND (' + domain1 + ')',
                        red_ids + domain2)
                writable_ids.extend(x[0] for x in cursor.fetchall())
        else:
            writable_ids = ids
        writable_ids = set(writable_ids)

        if fields_names is None:
            fields_names = []
        fields_names = fields_names[:]
        to_remove = set()
        for field in ('classification', 'calendar', 'transp'):
            if field not in fields_names:
                fields_names.append(field)
                to_remove.add(field)
        res = super(Event, self).read(cursor, user, ids,
                fields_names=fields_names, context=context)
        for record in res:
            if record['classification'] == 'private' \
                    and record['id'] not in writable_ids:
                self._clean_private(cursor, user, record, record['transp'],
                        context=context)
            for field in to_remove:
                del record[field]
        if int_id:
            return res[0]
        return res

    def write(self, cursor, user, ids, values, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if len({}.fromkeys(ids)) != self.search(cursor, user,
                [('id', 'in', ids)], context=context, count=True):
            self.raise_user_error(cursor, 'access_error',
                    self._description, context=context)
        res = super(Event, self).write(cursor, user, ids, values,
                context=context)
        if len({}.fromkeys(ids)) != self.search(cursor, user,
                [('id', 'in', ids)], context=context, count=True):
            self.raise_user_error(cursor, 'access_error',
                    self._description, context=context)
        return res

    def delete(self, cursor, user, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if len({}.fromkeys(ids)) != self.search(cursor, user,
                [('id', 'in', ids)], context=context, count=True):
            self.raise_user_error(cursor, 'access_error',
                    self._description, context=context)
        return super(Event, self).delete(cursor, user, ids, context=context)

Event()
