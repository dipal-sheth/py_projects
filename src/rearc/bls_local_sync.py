#!/usr/bin/env python3
import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# BLS requires User-Agent with contact info
HEADERS = {
    "User-Agent": "BLSDataSync/1.0 (dip2002@gmail.com)"
}

def list_remote_files(base_url):
    """Scrape the directory listing for available files."""
    resp = requests.get(base_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href or href in ("../",):
            continue
        file_url = urljoin(base_url, href)
        links.append((href, file_url))
    return links

def needs_download(file_url, local_path):
    """Check if file needs to be downloaded (not present or size mismatch)."""
    try:
        head = requests.head(file_url, headers=HEADERS, timeout=30, allow_redirects=True)
        head.raise_for_status()
        remote_size = int(head.headers.get("Content-Length", -1))
    except Exception:
        return True  # if HEAD fails, attempt download

    if not os.path.exists(local_path):
        return True

    local_size = os.path.getsize(local_path)
    return local_size != remote_size

def download_file(file_url, local_path):
    """Download a single file."""
    try:
        response = requests.get(file_url, headers=HEADERS, timeout=60, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {local_path}")
    except Exception as e:
        print(f"Failed to download {file_url}: {e}")

def sync_files(base_url, dest_dir, concurrency=4, delete=False):
    """Sync files from BLS site to local directory."""
    remote_files = list_remote_files(base_url)
    remote_names = {name for name, _ in remote_files}

    # download/update files
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {}
        for name, url in remote_files:
            local_path = os.path.join(dest_dir, name)
            if needs_download(url, local_path):
                futures[executor.submit(download_file, url, local_path)] = name

        for future in as_completed(futures):
            future.result()

    # delete local files not in remote
    if delete:
        for root, _, files in os.walk(dest_dir):
            for f in files:
                if f not in remote_names:
                    local_path = os.path.join(root, f)
                    os.remove(local_path)
                    print(f"Deleted stale file: {local_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync BLS files to local directory")
    parser.add_argument("--base-url", required=True, help="Base URL of BLS dataset")
    parser.add_argument("--dest-dir", required=True, help="Destination local directory")
    parser.add_argument("--concurrency", type=int, default=4, help="Number of parallel downloads")
    parser.add_argument("--delete", action="store_true", help="Delete local files not in remote")

    args = parser.parse_args()
    sync_files(args.base_url, args.dest_dir, args.concurrency, args.delete)
