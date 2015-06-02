#!/usr/bin/env python
import sys
import subprocess
import re
from collections import OrderedDict

PKCS11_URL_PREFIX = 'pkcs11:'


class Pkcs11Object(object):
    def __init__(self, id, typename='Object'):
        self.attrs = {}
        self.id = id
        self.memo = {}
        self.typename = typename

    def get_str(self, exclude_attrs=()):
        s = '{0} {1}:\n'.format(self.typename, self.id)
        for k,v in self.attrs.iteritems():
            if k in exclude_attrs: continue
            if not v: continue
            s += '  {0}: {1}\n'.format(k, v)
        return s

    def __str__(self):
        return self.get_str()

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

    def get_url(self, components):
        s = ';'.join('{0}={1}'.format(k,v) for k,v in self.url_dict().iteritems() if k in components)
        return PKCS11_URL_PREFIX + s



class Token(Pkcs11Object):
    def __init__(self, id):
        super(Token, self).__init__(id, 'Token')

class Certificate(Pkcs11Object):
    def __init__(self, id):
        super(Certificate, self).__init__(id, 'Certificate')


class P11Tool(object):
    def __init__(self):
        self.p11tool = 'p11tool'

    def _get_objects(self, args, objname, objtype):
        p = subprocess.Popen(
                args = [self.p11tool] + args,
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


    def get_tokens(self):
        args = ['--list-tokens']
        return self._get_objects(args, 'Token', Token)

    def get_certs(self, url=None):
        args = ['--list-certs']
        if url:
            args.append(url)
        return self._get_objects(args, 'Object', Certificate)


def input_int(prompt):
    while True:
        res = raw_input(prompt)
        if res:
            try:
                return int(res)
            except ValueError:
                print 'Invalid input'


def select_token(p11):
    print 'Finding hardware tokens...'
    hw_tokens = [t for t in p11.get_tokens() \
                 if t['type'] == 'Hardware token']

    if not hw_tokens:
        print 'No hardware tokens found.'
        print 'Is your reader connected and smart card inserted?'
        return None

    if len(hw_tokens) == 1:
        return hw_tokens[0]

    print '\nSelect the hardware token that is your CAC:'
    for t in hw_tokens:
        print t

    while True:
        tokn = input_int('Token #? ')

        for t in hw_tokens:
            if t.id == tokn:
                return t
        else:
            print 'No hardware token by that number'


def select_cert(p11, token):
    print '\nFinding token certificates...'
    certs = p11.get_certs(token.min_url())

    if not certs:
        print 'No certificates found on token'
        return 1

    if len(certs) == 1:
        return certs[0]

    print '\nSelect the certificate to use for VPN authentication:'
    for c in certs:
        print c.get_str(exclude_attrs=('url'))

    while True:
        certn = input_int('Certificate #? ')

        for c in certs:
            if c.id == certn:
                return c
        else:
            print 'No certificate by that number'

def main():
    p11= P11Tool()

    token = select_token(p11)
    if not token:
        return 1
    #print '\nCAC PKCS11 URL: ', token.min_url()

    cert = select_cert(p11, token)
    if not cert:
        return 1
    cert_url = cert.get_url(('token','id'))
    #print '\nCertificate URL: ', cert_url

    print '\n\nUse the following command to start the VPN:'
    print 'sudo openconnect -c \'{0}\' vpn.example.com'.format(cert_url)

    return 0

    

if __name__ == '__main__':
    try:
        rc = main()
    except KeyboardInterrupt:
        rc = 33
    sys.exit(rc)
