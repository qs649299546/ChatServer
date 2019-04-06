from concurrent.futures import ThreadPoolExecutor

import oss2

from settings import SITE_SETTINGS, OSS2_SETTINGS


auth = oss2.Auth(OSS2_SETTINGS['access_key_id'], OSS2_SETTINGS['access_key_secret'])
bucket = oss2.Bucket(auth, OSS2_SETTINGS['endpoint'], OSS2_SETTINGS['bucket_name'])
executor = ThreadPoolExecutor()


# def upload(data, key):
#     response = bucket.put_object(key, data)
#     return response

def upload(data, key):
    future = executor.submit(bucket.put_object, key, data)
    return future


def avatar_url(key, default=SITE_SETTINGS['default_avatar']):
    if key:
        return OSS2_SETTINGS['domain'] + key
    else:
        return default


def logo_url(key, default=SITE_SETTINGS['default_corp_logo']):
    if key:
        return OSS2_SETTINGS['domain'] + key
    else:
        return default

