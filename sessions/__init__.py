#!/usr/bin/env python
#
# Copyright 2009 unscatter.com
#
# This source code is proprietary and owned by jbowman and may not
# be copied, distributed, or run without prior permission from the owner.

__author__="jbowman"
__date__ ="$Oct 27, 2009 6:57:55 PM$"

import memcache
import datetime
import settings
from time import strftime
import hashlib
import time
import random

class Session(object):
    """
    Session class, used to manage persistence across multiple requests. Uses
    a memcached backend and Cookies.
    """

    def __init__(self, cookie_path=settings.session["DEFAULT_COOKIE_PATH"],
            cookie_name=settings.session["COOKIE_NAME"],
            set_cookie_expires=settings.session["SET_COOKIE_EXPIRES"],
            session_token_ttl=settings.session["SESSION_TOKEN_TTL"],
            session_expire_time=settings.session["SESSION_EXPIRE_TIME"],
            memcache_url=settings.session["MEMCACHE_URL"],
            req_obj = False):
        """
        __init__ loads the session, checking the browser for a valid session
        token. It will either validate the session and/or create a new one
        if necessary.
        """

        self.mc = memcache.Client(memcache_url, debug=0)

        # If session is being used on this page view, then go ahead
        # and make the page not cacheable. This makes sure the user
        # gets their dynamic content.
        # print self.no_cache_headers()

        # self.cache is used to avoid unnecessary repeated access to the
        # memcache. As keys are pulled, they are cached in local memory for
        # the request, in case they are used multiple times.
        self.cache = {}

        # check the cookie

        new_session = True
        do_put = False

        cookie = req_obj.get_cookie(cookie_name)

        if cookie:
            (sid, token) = cookie.split("-")
            self.session = self.mc.get(sid)
            if self.session:
                if token in self.session["tokens"]:
                    new_session = False

        if new_session:
            sid = self.new_sid()
            self.session = {"sid": sid.encode("ascii"),
                "tokens": [self.new_sid()],
                "last_token_update": datetime.datetime.now(),
                "data": {}}
            do_put = True
            cookie = "%s-%s" % (sid, self.session["tokens"][-1])

            self.cache[u"sid"] = self.session["sid"]
        else:
            duration = datetime.timedelta(seconds=session_token_ttl)
            session_age_limit = datetime.datetime.now() - duration
            if self.session['last_token_update'] < session_age_limit:
                token = self.new_sid()
                if len(self.session['tokens']) > 2:
                    self.session['tokens'].pop(0)
                self.session['tokens'].insert(0,token)
                self.session["last_token_update"] = datetime.datetime.now()
                cookie = "%s-%s" % (sid, self.session["tokens"][0])
                do_put = True

        req_obj.set_cookie(name = cookie_name, value = cookie)

        if do_put:
            self.mc.set(self.session['sid'].encode("ascii"), self.session)

    def new_sid(self):
        """
        Create a new session id or token.

        Returns session id/token as a unicode string.
        """
        sid = u"%s" % (hashlib.md5(repr(time.time()) + \
            unicode(random.random())).hexdigest()
        )
        return sid


    def no_cache_headers(self):
        """
        Generates headers to avoid any page caching in the browser.
        Useful for highly dynamic sites.

        Returns a unicode string of headers.
        """
        return u"".join([u"Expires: Tue, 03 Jul 2001 06:00:00 GMT",
            strftime("Last-Modified: %a, %d %b %y %H:%M:%S %Z").decode("utf-8"),
            u"Cache-Control: no-store, no-cache, must-revalidate, max-age=0",
            u"Cache-Control: post-check=0, pre-check=0",
            u"Pragma: no-cache",
        ])


    def delete(self):
        return self.mc.delete(self.session["sid"])

    def has_key(self, keyname):
        return self.__contains__(keyname)

    def save(self):
        self.mc.set(self.session["sid"], self.session)

    def __delitem__(self, key):
        del self.session["data"][key]
        self.mc.set(self.session["sid"], self.session)
        return True


    def __getitem__(self, key):
        return self.session["data"][key]

    def __setitem__(self, key, val):
        self.session["data"][key] = val
        self.mc.set(self.session["sid"].encode("ascii"), self.session)
        return True

    def __len__(self):
        return len(self.session["data"])

    def __contains__(self, key):
        return self.session["data"].has_key(key)

    def __iter__(self):
        for key in self.session["data"]:
            yield key

    def __str__(self):
        return u"{%s}" % ', '.join(['"%s" = "%s"' % (k, self.session["data"][k]) for k in self.session["data"]])

