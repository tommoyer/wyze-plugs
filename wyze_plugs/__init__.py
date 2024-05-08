import sys
import logging
import os
import toml
import pathlib

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

logging.basicConfig(level=logging.WARN)


def toggle(client, config, device_id):
    try:
        plug = client.plugs.info(device_mac=device_id)
        if plug.is_on:
            print(f'plug {device_id} is listed as on')
            client.plugs.turn_off(device_mac=plug.mac, device_model=plug.product.model)
        else:
            print(f'plug {device_id} is listed as off')
            client.plugs.turn_on(device_mac=plug.mac, device_model=plug.product.model)
    except WyzeApiError as e:
        # You will get a WyzeApiError if the request failed
        print(f'Got an error: {e}')


def main():
    if len(sys.argv) < 2:
        print('Not enough arguments')
        sys.exit(-1)

    config_file = pathlib.Path(os.environ['HOME'], '.config/wyze-plugs/config.toml')

    if not config_file.exists():
        print(f'Config file ({config_file}) does not exist')
        sys.exit(-1)

    with open(config_file, 'r') as config_file_handle:
        config = toml.load(config_file_handle)

    client = Client(
        email=os.environ['WYZE_EMAIL'],
        password=os.environ['WYZE_PASSWORD'],
        key_id=os.environ['WYZE_ID'],
        api_key=os.environ['WYZE_KEY'],
        totp_key=os.environ['WYZE_TOTP_KEY']
    )

    if sys.argv[1].strip() == 'device-list':
        print('Configured Devices:')
        for device_name in config['devices'].keys():
            print(f' - {device_name}')

        print('Registered Devices:')
        for device in client.devices_list():
            print(f'- nickname: {device.nickname}')
            print(f'  - mac: {device.mac}')
            print(f'  - is_online: {device.is_online}')
            print(f'  - product model: {device.product.model}\n')
        sys.exit(0)

    try:
        toggle(client, config, config['devices'][sys.argv[1].strip()])
    except KeyError as e:
        print(f'Unknown device {sys.argv[1].strip()}')
        print(e)


if __name__ == '__main__':
    main()
