#!/opt/asset-munki/.venv/bin/python

import os
import sys
import csv
from datetime import datetime
import requests
import logging

from assetmunki import AssetMunki
from assetmunki.cli import cli
from assetmunki.util import format_bytes,\
    get_filename_for_model_img,\
    download_images_from_serials,\
    get_category_name
from assetmunki.ext.munki import MunkiReportIntegration
from assetmunki.ext.snipeit import SnipeIntegration, dto as snipe_dtos
from assetmunki.ext.snipeit.exceptions import SnipeITAssetNotFoundError

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


PRODUCT_IMG_SAVE_ROOT = os.getenv('SNIPEIT_PUBLIC_UPLOADS_DIR', '/var/www/snipeit/public/uploads/models/')


DEFAULT_MFG_ID = 2 # Apple
DEFAULT_FIELDSET_ID = 2 # AppleCare
DEFAULT_COMPANY_ID = 1 # TRBC
DEFAULT_STATUS_ID = 1 # Pending


munkireport = MunkiReportIntegration()
snipeit = SnipeIntegration()


def create_assetmunki():
    assetmunki = AssetMunki()
    munkireport.init_assetmunki(assetmunki)
    snipeit.init_assetmunki(assetmunki)
    return assetmunki


# (1) Asset with MAC Address: [<Field MAC Address>]
# (2) Asset with Warranty: [<Field Warranty Start>, <Field Warranty Thru>, <Field RAM>, <Field Storage>, <Field CPU>]
# (3) Asset with AppleCare: [<Field AppleCare ID>, <Field AppleCare Invoice #>, <Field Warranty Start>, <Field Warranty Thru>, <Field RAM>, <Field Storage>, <Field CPU>]


def snipeit_payload_from_mr(snipeit_data, mr_data, is_new=True):
    try:
        start_date = datetime.strptime(mr_data['purchase_date'], '%Y-%m-%d')
    except:
        start_date = None

    try:
        end_date = datetime.strptime(mr_data['end_date'], '%Y-%m-%d')
    except:
        end_date = None

    try:
        months_coverage = ((end_date.year - start_date.year)*12)
    except:
        months_coverage = 0

    fieldset = snipeit.client.get_fieldsets()[DEFAULT_FIELDSET_ID]
    merge = {
        'name': f"{mr_data['hostname']}",
        'serial': mr_data['serial_number'],
        'asset_tag': mr_data['serial_number'],
        'warranty_months': months_coverage,
        fieldset.fields[6].db_column_name: mr_data['cpu'],
        fieldset.fields[5].db_column_name: f"{format_bytes(int(mr_data['totalsize']))} {mr_data['media_type'].upper()}",
        fieldset.fields[4].db_column_name: f"{mr_data['physical_memory']} GB",
        fieldset.fields[2].db_column_name: mr_data['purchase_date'],
        fieldset.fields[3].db_column_name: mr_data['end_date']
    }
    
    if not is_new:
        del merge['asset_tag']
    
    return {**snipeit_data, **merge}


def run_migration():
    serial_numbers = []

    query = munkireport.client.get_assets()
    categories = snipeit.client.get_categories()
    
    for mra in query:
        hostname = mra['hostname']
        mra_category = None

        if mra['serial_number'] not in serial_numbers:
            serial_numbers.append(mra['serial_number'])
        else:
            continue

        category_name = get_category_name(mra['machine_name'])
        
        for category in categories:
            if category.name.lower() == category_name:
                mra_category = category
                break

        model_id = snipeit.client.get_model_id(mra['machine_model'])

        if not model_id:
            model_payload = {
                'name': mra['machine_desc'],
                'model_number': mra['machine_model'],
                'category_id': mra_category.id,
                'manufacturer_id': DEFAULT_MFG_ID,
                'fieldset_id': DEFAULT_FIELDSET_ID,
                'image': get_filename_for_model_img(mra['serial_number'])
            }

            response = snipeit.client.post_model(model_payload)
            if response['status'] == 'success':
                model_id = response['payload']['id']
                logger.info(f'added new model: {model_id}')
            else:
                logger.warning(f"{response['status']}: {response['message']}")
        else:
            existing_model = snipeit.client.get_model(model_id)
            if mra_category.id != existing_model.category.id:
                response = snipeit.client.update_model(existing_model.id, {
                    'category_id': mra_category.id
                })
                if response['status'] == 'success':
                    logger.info(f'Updated model category: {existing_model.id}')
                else:
                    logger.warning(f"{response['status']}: {response['message']}")

        try:
            existing_asset = snipeit.client.get_asset_by_serial(mra['serial_number'])

            if existing_asset.model.id != model_id or existing_asset.name != hostname:
                asset_payload_data = {
                    'model_id': model_id
                }

                asset_payload = snipeit_payload_from_mr(asset_payload_data, mra, False)
                response = snipeit.client.update_asset(existing_asset.id, asset_payload)
                if response['status'] == 'success':
                    logger.info(f"{response['messages']}: {response['payload']['id']}")
                else:
                    logger.error(existing_asset)
                    logger.error(response)
                    logger.warning(f"Could not save asset:")
                    for rk in response['messages']:
                        logger.warning(f"\t{response['messages'][rk][0]}")
        except SnipeITAssetNotFoundError as snipe_dne:
            made_request = True
            status_id = DEFAULT_STATUS_ID

            asset_payload_data = {
                'company_id': DEFAULT_COMPANY_ID,
                'model_id': model_id,
                'status_id': status_id
            }

            asset_payload = snipeit_payload_from_mr(asset_payload_data, mra)

            response = snipeit.client.post_asset(asset_payload)
            if response['status'] == 'success':
                logger.info(f"{response['messages']}: {response['payload']['id']}")
            else:
                logger.warning(f"Could not save asset:")
                for rk in response['messages']:
                    logger.warning(f"\t{response['messages'][rk][0]}")

    try:
        download_images_from_serials(serial_numbers)
    except FileNotFoundError as f_dne:
        logger.error(f_dne)


def match_asset_tags(filename):
    pairs = []

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if not row[0]:
                continue
            if row[0][:2] != 'TR':
                continue
            pairs.append((row[1], row[0]))
    
    for p in pairs:
        try:
            asset = snipeit.client.get_asset_by_serial(p[0])

            if asset.asset_tag == p[1]:
                continue

            logger.info(f'Setting asset {asset.id}\'s asset tag: {p[1]}')
            
            asset_payload = {
                'asset_tag': p[1]
            }

            response = snipeit.client.update_asset(asset.id, asset_payload)
        except SnipeITAssetNotFoundError as snipe_dne:
            continue


def main(argv):
    ''' Main entry point into the program '''

    logger.info('\nAsset-Munki Utility\nBy Steven Floyd\n')

    (args, parser) = cli(argv)

    try:
        assetmunki = create_assetmunki()
    except Exception as e:
        raise e

    logger.info('Enabled integrations:')
    for i in assetmunki.integrations:
        logger.info (f'\t{i}')

    logger.info('\n------------------------------------------------------------')
    print('Migrating assets from Munki Report...')
    run_migration()
    logger.info('\n------------------------------------------------------------')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
