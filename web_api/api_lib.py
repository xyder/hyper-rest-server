import json

import requests


class HttpMethods:
    """
    Const struct to store HTTP methods keywords
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


class HttpStatus:
    OK = {
        'status': 'OK',
        'status_code': 200
    }
    NOT_FOUND = {
        'status': 'Not found.',
        'status_code': 404
    }

    BAD_REQUEST = {
        'status': 'Bad request.',
        'status_code': 400
    }


class Link(object):
    def __init__(self, rel='', href='', method=HttpMethods.GET, args=None):
        self.rel = rel
        self.url = href
        self.method = method
        self.args = args

    def create_function(self):
        def f(args=None):
            args = getattr(args, 'to_dict', args)
            return requests.request(self.method, self.url, json=args).json()

        return f

    def to_dict(self):
        ret_dict = {
            'rel': self.rel,
            'href': self.url,
            'method': self.method
        }
        if self.args is not None:
            ret_dict['args'] = self.args

        return ret_dict


def create_link(link_dict=None):
    def f(args=None):
        # prioritize o.to_dict if available
        args = getattr(args, 'to_dict', args)
        resp = requests.request(link_dict['method'], link_dict['href'], json=args)
        return resp.json()

    return f


class ApiObject(object):
    def __init__(self, **kwargs):
        self.attributes = []
        self.links = {}
        json_string = kwargs.get('json')
        if json_string:
            self.from_json(json_string)
        else:
            self.from_dict(kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        ret_dict = {}

        for attribute in self.attributes:
            attr = getattr(self, attribute)
            try:
                if isinstance(attr, list):
                    ret_dict[attribute] = []
                    for item in attr:
                        ret_dict[attribute].append(item.to_dict())
                else:
                    ret_dict[attribute] = attr.to_dict()
            except AttributeError:
                ret_dict[attribute] = attr

        ret_dict['_links'] = []

        for link in self.links:
            ret_dict['_links'].append(self.links[link].to_dict())

        return ret_dict

    def from_dict(self, dictionary=None):
        if isinstance(dictionary, dict):
            links = dictionary.pop('_links', [])
            for k, v in dictionary.items():
                self.attributes.append(k)
                setattr(self, k, v)

            for l in links:
                link = l if isinstance(l, Link) else Link(**l)
                self.links[link.rel] = link
                setattr(self, '%s_link' % link.rel, link.create_function())

    def from_json(self, json_string=''):
        self.from_dict(json.loads(json_string))

    def __getattr__(self, attr):
        """
        Dummy method to fool PyCharm regarding missing attributes and methods
        """
        raise AttributeError(attr)


class Page(ApiObject):
    def __init__(self, **kwargs):
        init_json = {
            'data': kwargs.get('payloads', []),
            'record_count': kwargs.get('record_count', 0),
            'status': kwargs.get('status', HttpStatus.OK['status']),
            'status_code': kwargs.get('status_code', HttpStatus.OK['status_code'])
        }
        super(Page, self).__init__(**init_json)


class Payload(ApiObject):
    def __init__(self, **kwargs):
        url = kwargs.get('url', '')
        init_json = {
            'tasks': kwargs.get('items', []),
            '_links': [
                Link('self', url),
                Link('add', url, method=HttpMethods.POST, args=[]),
                Link('list', '%s/list' % url)
            ]
        }
        super(Payload, self).__init__(**init_json)


class Item(ApiObject):
    def __init__(self, **kwargs):
        url = kwargs.get('url', '')
        init_json = {
            'title': kwargs.get('title', ''),
            'task_id': kwargs.get('task_id', ''),
            'body': kwargs.get('body', ''),
            'state': kwargs.get('state', 'open'),
            'created': kwargs.get('created', 0),
            'due': kwargs.get('due', 0),
            '_links': [
                Link('self', url),
                Link('update', url, HttpMethods.POST, args=[]),
                Link('delete', url, HttpMethods.DELETE)
            ]
        }
        super(Item, self).__init__(**init_json)

    def get_clean_attributes(self):
        return {k: getattr(self, k) for k in self.attributes if k != 'task_id'}
