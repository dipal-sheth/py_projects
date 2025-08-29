import requests
import os
import re
from bs4 import BeautifulSoup

SOURCE_URL = 'http://download.bls.gov/pub/time.series/pr/'
LOCAL_DIR = 'src/rearc/data/bls_data'
USER_AGENT = 'dipal1712@gmail.com Python sync script (for BLS policy compliance)'

def list_remote_files():
    resp = requests.get(SOURCE_URL, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(resp.text, 'html.parser')
    files = {}
    for link in soup.find_all('a', href=True):
        fname = link['href']
        if re.match(r'^pr\\.', fname):
            head = requests.head(SOURCE_URL + fname, headers={'User-Agent': USER_AGENT}, allow_redirects=True)
            size = int(head.headers.get('Content-Length', 0))
            files[fname] = size
    return files

def list_local_files():
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)
    return {f: os.path.getsize(os.path.join(LOCAL_DIR, f)) for f in os.listdir(LOCAL_DIR)
            if os.path.isfile(os.path.join(LOCAL_DIR, f))}

def sync():
    remote_files = list_remote_files()
    local_files = list_local_files()

    # Download new or updated files
    for fname, rsize in remote_files.items():
        local_path = os.path.join(LOCAL_DIR, fname)
        if fname not in local_files or local_files[fname] != rsize:
            print(f'Downloading {fname}...')
            with requests.get(SOURCE_URL + fname, headers={'User-Agent': USER_AGENT}, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    # Delete files not present in remote
    for fname in local_files:
        if fname not in remote_files:
            print(f'Deleting {fname}...')
            os.remove(os.path.join(LOCAL_DIR, fname))

if __name__ == '__main__':
    sync()
