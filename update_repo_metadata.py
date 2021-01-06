"""
Used as part of the CI scripts to set BinTray package version metadata

Requires the requests library
"""
import argparse
import json
import os
import sys
from datetime import datetime

import dateutil.parser
import requests
from dateutil import tz
from requests.auth import HTTPBasicAuth


class Updater:

    def __init__(self, conan_username: str, conan_password: str, package: str, version: str, channel: str):
        self.username = conan_username
        self.auth = HTTPBasicAuth(conan_username, conan_password)
        self.package = package
        self.version = version
        self.channel = channel

    def get_tag_info(self) -> dict:
        r = requests.get('https://invent.kde.org/api/v4/projects/frameworks%2fextra-cmake-modules/repository/tags/v{}'
                         .format(self.version), headers={'Accept': 'application/json'})
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.text:
                print(r.text)
            raise e
        return r.json()

    def update_package_version(self, data: dict, released: datetime):
        # BinTray API doesn't properly support ISO timestamps (requires microseconds even if 0, no TZ offset support)
        # so build it manually
        data['released'] = released.astimezone(tz.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        r = requests.patch(
            'https://api.bintray.com/packages/{user}/conan-packages/{package}:{user}/versions/{version}:{channel}'
                .format(package=self.package, user=self.username, version=self.version, channel=self.channel),
            auth=self.auth, json=data, headers={'Accept': 'application/json'})
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.text:
                print(r.text)
            raise e
        return r.json()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Update BinTray Conan repo with package version metadata')
    argparser.add_argument('--username', required=True, type=str, help='BinTray API username')
    argparser.add_argument('--password-env-var', required=True, type=str,
                           help='Environment variable to take the password from')
    argparser.add_argument('--package', required=True, type=str, help='Package name')
    argparser.add_argument('--version', required=True, type=str, help='Package version')
    argparser.add_argument('--channel', required=True, type=str, help='Package channel')
    argparser.add_argument('data', type=lambda json_str: json.loads(json_str),
                           help='Package metadata as a JSON dict, not including release date')
    args = argparser.parse_args()

    password = os.getenv(args.password_env_var)
    if password is None:
        print('No password defined in environment variable {}'.format(args.password_env_var), file=sys.stderr)
        exit(1)
    updater = Updater(args.username, password, args.package, args.version, args.channel)
    tag_info = updater.get_tag_info()
    updater.update_package_version(data=args.data, released=dateutil.parser.isoparse(tag_info['commit']['created_at']))

    exit(0)
