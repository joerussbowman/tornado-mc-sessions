#!/usr/bin/env python
#
# Copyright 2009 unscatter.com
#
# This source code is proprietary and owned by jbowman and may not
# be copied, distributed, or run without prior permission from the owner.

__author__="jbowman"
__date__ ="$Oct 27, 2009 9:20:35 PM$"


session = {
    "COOKIE_NAME": "unscatter_session",
    "DEFAULT_COOKIE_PATH": "/",
    "SESSION_EXPIRE_TIME": 7200,    # sessions are valid for 7200 seconds
                                    # (2 hours)
    "SET_COOKIE_EXPIRES": True,     # Set to True to add expiration field to
                                    # cookie
    "SESSION_TOKEN_TTL": 5,         # Number of seconds a session token is valid
                                    # for.
    "UPDATE_LAST_ACTIVITY": 60,     # Number of seconds that may pass before
                                    # last_activity is updated
    "MEMCACHE_URL": ['127.0.0.1:11211']
}
