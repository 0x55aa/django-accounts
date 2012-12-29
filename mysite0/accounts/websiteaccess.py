# -*- coding: utf-8 -*-

import json,time,urllib,urllib2,urlparse

QQ_APP_KEY = '100290185'
QQ_APP_SECRET = '70313357109904b393ec25edd79e2378'
QQ_CALLBACK_URL = 'http://talkqq.duapp.com/callback/qq/'
QQ_DOMAIN = 'graph.qq.com'

WEIBO_APP_KEY = '3245369781'
WEIBO_APP_SECRET = 'a392386089d470fdbd4aa03a6d026fbf'
WEIBO_CALLBACK_URL = 'http://talkqq.duapp.com/callback/weibo/'
WEIBO_DOMAIN = 'api.weibo.com'


def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o

class APIError(StandardError):
    '''
    raise APIError if got failed json message.
    '''
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
        
def _encode_params(**kw):
    '''
    Encode parameters.
    '''
    args = []
    for k, v in kw.iteritems():
        qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
        args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)

def _encode_multipart(**kw):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            ext = ''
            filename = getattr(v, 'name', '')
            n = filename.rfind('.')
            if n != (-1):
                ext = filename[n:].lower()
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % _guess_content_type(ext))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary

_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2

def _http_post(url, authorization=None, **kw):
    return _http_call(url, _HTTP_POST, authorization, **kw)

def _http_call(url, method, authorization, **kw):
    '''
    send an http request and expect to return a json object if no error.
    '''
    params = None
    boundary = None
    if method==_HTTP_UPLOAD:
        params, boundary = _encode_multipart(**kw)
    else:
        params = _encode_params(**kw)
    http_url = '%s?%s' % (url, params) if method==_HTTP_GET else url
    http_body = None if method==_HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    if authorization:
        req.add_header('Authorization', 'OAuth2 %s' % authorization)
    if boundary:
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    resp = urllib2.urlopen(req)
    body = resp.read()
    return body

#这个函数还有问题，qq的errorcode没有写
def return_data(data,logintype):
    if logintype == 'weibo':

        r = json.loads(data, object_hook=_obj_hook)
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, getattr(r, 'error', ''), getattr(r, 'request', ''))
        return r
    else:
        result = urlparse.parse_qs(data, True)
        access_token = str(result['access_token'][0])
        expires_in = float(int(result['expires_in'][0]) + int(time.time()))
        ajson = json.dumps({'access_token':access_token, 'expires_in': expires_in})
        r = json.loads( ajson, object_hook=_obj_hook)
        return r

class HttpObject(object):

    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            if self.client.is_expires():
                raise APIError('21327', 'expired_token', attr)
            return _http_call('%s%s.json' % (self.client.api_url, attr.replace('__', '/')), self.method, self.client.access_token, **kw)
        return wrap


class APIClient(object):
    '''
    API client using synchronized invocation.
    '''
    def __init__(self, logintype='', version='2'):
        if logintype == 'qq':
            self.client_id = QQ_APP_KEY
            self.client_secret = QQ_APP_SECRET
            self.redirect_uri = QQ_CALLBACK_URL
            self.auth_url = 'https://%s/oauth2.0/' % QQ_DOMAIN
            self.gettoken_url = '%s%s' % (self.auth_url, 'token')
        else:
            self.client_id = WEIBO_APP_KEY
            self.client_secret = WEIBO_APP_SECRET
            self.redirect_uri = WEIBO_CALLBACK_URL
            self.auth_url = 'https://%s/oauth2/' % WEIBO_DOMAIN
            self.gettoken_url = '%s%s' % (self.auth_url, 'access_token')

        self.logintype = logintype 
        self.response_type = 'code'
        #用户唯一标识
        self.uid = None
        #self.api_url = 'https://%s/%s/' % (domain, version)
        self.access_token = None
        self.expires = 0.0
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)
        self.upload = HttpObject(self, _HTTP_UPLOAD)

    def set_access_token(self, access_token, expires_in, userid):
        self.access_token = str(access_token)
        self.expires = float(expires_in)
        self.uid = str(userid)

    def get_authorize_url(self):
        '''
        return the authroize url that should be redirect.
        '''
        return '%s%s?%s' % (self.auth_url, 'authorize', \
                _encode_params(client_id = self.client_id, \
                        response_type = 'code', \
                        redirect_uri = self.redirect_uri))

    def request_access_token(self, code):
        '''
        return access token as object: {"access_token":"your-access-token","expires_in":12345678}, expires_in is standard unix-epoch-time
        '''
        body = _http_post(self.gettoken_url, \
                client_id = self.client_id, \
                client_secret = self.client_secret, \
                redirect_uri = self.redirect_uri, \
                code = code, grant_type = 'authorization_code')
        #统一返回数据的格式
        r = return_data(body,self.logintype)
        r.expires_in += int(time.time())
        return r

    #获取qq登录的OpenID
    def request_qq_uid(self, access_token):
        """
        获取qq登录的OpenID
        """
        body = _http_post("%sme" % (self.auth_url), \
                access_token = access_token)
        r = body.split('"')[7]
        return r
        


    def is_expires(self):
        return not self.access_token or time.time() > self.expires

    def __getattr__(self, attr):
        return getattr(self.get, attr)
