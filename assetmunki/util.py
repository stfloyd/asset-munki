import logging
import requests
from typing import List
from pathlib import Path


logger = logging.getLogger(__name__)


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size} {power_labels[n]+'B'}"


def get_filename_for_model_img(serial: str):
    last4 = serial[len(serial)-4:]
    dl_url = f'https://km.support.apple.com/kb/securedImage.jsp?configcode={last4}&size=960x960'
    r = requests.get(dl_url, allow_redirects=True)
    return r.url.split('/')[-1]


def download_images_from_serials(location: str, serials: List[str]):
    # https://km.support.apple.com/kb/securedImage.jsp?configcode=[[last 4 of serial]]&size=960x960
    save_path = Path(location).absolute()
    finished = []
    for serial in serials:
        last4 = serial[len(serial)-4:]
        if last4 in finished:
            continue
        dl_url = f'https://km.support.apple.com/kb/securedImage.jsp?configcode={last4}&size=960x960'
        r = requests.get(dl_url, allow_redirects=True)
        filename = r.url.split('/')[-1]
        location = save_path.joinpath(filename)
        open(f'{location}{filename}', 'wb').write(r.content)
        finished.append(last4)
    logger.info(f'Fetched {len(finished)} images for model(s) @ \'{location}\'')


def get_category_name(machine_name: str):
    machine_name_l = machine_name.lower()
    if machine_name_l == 'imac' or machine_name_l == 'mac mini':
        return 'desktops'
    elif machine_name_l == 'macbook' or machine_name_l == 'macbook pro' or machine_name_l == 'macbook air':
        return 'laptops'
    else:
        return 'unknown'
