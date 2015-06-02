#!/usr/bin/env python
import sys
import subprocess
import re
import shlex
from collections import OrderedDict

PKCS11_URL_PREFIX = 'pkcs11:'


class Pkcs11Object(object):
    def __init__(self, id, typename='Object'):
        self.attrs = {}
        self.id = id
        self.memo = {}
        self.typename = 'Object'

    def __str__(self):
        s = '{1} {0}:\n'.format(self.typename, self.id)
        for k,v in self.attrs.iteritems():
            if v:
                s += '  {0}: {1}\n'.format(k, v)
        return s

    def __getitem__(self, k):
        k = k.lower()
        return self.attrs[k]

    def __setitem__(self, k, v):
        k = k.lower()
        if k in self.attrs:
            raise ValueError('Key {0} already exists'.format(k))
        self.attrs[k] = v

    def url_dict(self):
        url = self['url']

        if not url.startswith(PKCS11_URL_PREFIX):
            raise ValueError('Invalid PKCS#11 URL: "{0}"'.format(rl))
        url = url[len(PKCS11_URL_PREFIX):]

        def parts(url):
            for pair in url.split(';'):
                yield pair.split('=',1)

        # Preserve the original order of the URL
        return OrderedDict(parts(url))

    def min_url(self):
        s = ';'.join('{0}={1}'.format(k,v) for k,v in self.url_dict().iteritems() if v)
        return PKCS11_URL_PREFIX + s


class Token(Pkcs11Object):
    def __init__(self, id):
        super(Token, self).__init__(id, 'Token')

class Certificate(Pkcs11Object):
    def __init__(self, id):
        super(Certificate, self).__init__(id, 'Certificate')


def _get_p11tool_objects(args, objname, objtype):
    p = subprocess.Popen(
            args = ['p11tool'] + args,
            stdout = subprocess.PIPE)

    start_obj_pat = re.compile('^{0} (\d+)'.format(objname))

    objects = []
    curobj = None
    for line in p.stdout:
        line = line.strip()
        if not line: continue

        # New object?
        m = start_obj_pat.match(line)
        if m:
            if curobj:
                objects.append(curobj)
            curobj = objtype(int(m.group(1)))
            continue

        # Nope, keep adding to current object 
        k,v = line.split(':', 1)
        v = v.strip()
        curobj[k] = v

    if curobj:
        objects.append(curobj)

    return objects


def get_tokens():
    args = ['--list-tokens']
    return _get_p11tool_objects(args, 'Token', Token)

def get_certs(url):
    args = ['--list-certs', url]
    return _get_p11tool_objects(args, 'Object', Certificate)


def input_int(prompt):
    while True:
        res = raw_input(prompt)
        if res:
            try:
                return int(res)
            except ValueError:
                print 'Invalid input'



def main():
   
    print 'Finding hardware tokens...'
    hw_tokens = [t for t in get_tokens() \
                 if t['type'] == 'Hardware token']

    if not hw_tokens:
        print 'No hardware tokens found.'
        print 'Is your reader connected and smart card inserted?'
        return 1

    if len(hw_tokens) == 1:
        token = hw_tokens[0]
    else:
        print 'Select the hardware token that is your CAC:'
        for t in hw_tokens:
            print t

        while True:
            tokn = input_int('Token #? ')

            for t in hw_tokens:
                if t.id == tokn:
                    break
            else:
                print 'No hardware token by that number'
                continue
            token = t
            break

    url = token.min_url()
    print '\nCAC PKCS11 URL: ', url

    print '\nCAC Certificates:'
    certs = get_certs(url)
    for c in certs:
        print c



    return 0

    

if __name__ == '__main__':
    try:
        rc = main()
    except KeyboardInterrupt:
        rc = 33
    sys.exit(rc)
