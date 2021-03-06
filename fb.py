import contextlib
import json
from pprint import pprint
import time
import urllib
import urlparse
import webbrowser

from settings import *

def get_token():
    AUTH_URL = 'https://www.facebook.com/dialog/oauth'
    AUTH_URL_ARGS = {
        'client_id': 428109190573302 ,
        'redirect_uri': 'https://www.facebook.com/connect/login_success.html',
        'response_type': 'token',
        'scope': 'user_photos,friends_photos'
    }

    try:
        with open(CREDENTIALS, 'r') as f:
            response = json.load(f)
            if response['expires'] > time.time() + 1200: # 20 minutes
                return response['access_token']
    except:
        pass

    url = AUTH_URL + '?' + urllib.urlencode(AUTH_URL_ARGS)
    webbrowser.open(url)
    time.sleep(2)
    response = urlparse.parse_qs(raw_input('Your token?\t'))
    response = dict((k, v[0]) for k, v in response.iteritems())
    response['expires'] = int(response['expires_in']) + int(time.time())

    with open(CREDENTIALS, 'w') as f:
        json.dump(response, f)
    return response['access_token']

def get_photos():
    with open(META) as f:
        data = f.read()
    if data:
        redo = raw_input('meta.json already exists, are you sure you want to overwrite?')
        if redo.lower() != 'y':
            return

    PHOTOS_URL = 'https://graph.facebook.com/me/photos'
    args = {
        'access_token': get_token(),
        'limit': 200
    }
    url = PHOTOS_URL + '?' + urllib.urlencode(args)
    with contextlib.closing(urllib.urlopen(url)) as f:
        data = f.read()
    data = json.loads(data)
    photos_meta = []
    for i, tagged_photo in enumerate(data['data']):
        meta = {}
        meta['id']= tagged_photo['id']
        meta['tags'] = {'other': []}
        for tag in tagged_photo['tags']['data']:
            if tag['name'] == 'Eric Martin':  #fix me so hard
                meta['tags']['me'] = [tag['x'], tag['y']]
            else:
                meta['tags']['other'].append([tag['x'], tag['y']])
        picture_url = tagged_photo['images'][1]['source']

        with contextlib.closing(urllib.urlopen(picture_url)) as f:
            bits = f.read()

        filename = PICTURES + meta['id'] + '.jpg'
        with open(filename, 'w') as f:
            f.write(bits)

        meta['picture'] = filename

        photos_meta.append(meta)

    with open(META, 'w') as f:
        json.dump(photos_meta, f)

if __name__ == '__main__':
    get_photos()
