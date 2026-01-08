import json
from urllib.parse import quote

from ansible.module_utils.urls import open_url
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable

DOCUMENTATION = r"""
author: Tokuhiro Matsuno (@tokuhirom)
name: sacloud
short_description: Sacloud inventory source
version_added: 1.0.0
description:
  - Get inventory hosts from the sacloud.
extends_documentation_fragment:
  - constructed
options:
  url:
    description: Base URL to sacloud API.
    type: string
    default: 'https://secure.sakura.ad.jp/cloud/zone'
    env:
      - name: SAKURA_API_ROOT_URL
  access_token:
    description: Access token for sacloud API.
    type: string
    required: true
    env:
      - name: SAKURA_ACCESS_TOKEN
  access_token_secret:
    description: Access token secret for sacloud API.
    type: string
    required: true
    env:
      - name: SAKURA_ACCESS_TOKEN_SECRET
  zones:
    description: Populate inventory with instances in this zone.
    required: true
    type: list
    elements: string
  skip_group_tags:
    description: Do not create groups for these tags.
    default: ["@auto-reboot", "__with_sacloud_inventory"]
    type: list
    elements: string
"""

EXAMPLES = r"""
# sacloud.yml
plugin: sacloud
zones:
  - tk1b
  - is1a
skip_group_tags:
  - "@auto-reboot"
  - "__with_sacloud_inventory"
compose:
  ansible_host: user_ip_address[0] if inventory_hostname.startswith('fumidai.') else user_ip_address[1]

# 実行例
# ansible-inventory -i sacloud.yml --list
"""

# see https://docs.usacloud.jp/terraform/provider/


def get_sacloud_servers(api_root: str, zone: str, token: str, token_secret: str):
    q = r"""{"From":0,"To":0,"Sort":["Name"]}"""
    url = f"{api_root}/{zone}/api/cloud/1.1/server?" + quote(q, safe='')
    response = open_url(url, url_username=token, url_password=token_secret)
    data = response.read()

    result = json.loads(data)
    return result


# Construtable: https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_inventory.html
class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = "sacloud"

    def verify_file(self, path):
        valid = False
        if super().verify_file(path):
            if path.endswith("sacloud.yaml") or path.endswith("sacloud.yml"):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "sacloud.yaml" nor "sacloud.yml"')
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        self._read_config_data(path)

        api_root = self.get_option("url")
        access_token = self.get_option("access_token")
        access_token_secret = self.get_option("access_token_secret")
        zones = self.get_option("zones")

        skip_group_tags = self.get_option("skip_group_tags") or []

        compose = self.get_option("compose") or {}
        groups = self.get_option("groups") or {}
        keyed_groups = self.get_option("keyed_groups") or []

        self.display.vvv("Fetching sacloud inventory for zones: %s" % ",".join(zones))

        for zone in zones:
            servers = get_sacloud_servers(api_root, zone, access_token, access_token_secret)

            for server in servers["Servers"]:
                hostname = server["Name"]
                self.inventory.add_host(hostname)

                interfaces = server["Interfaces"]
                self.inventory.set_variable(hostname, "ip_address", [x.get("IPAddress") for x in interfaces])
                self.inventory.set_variable(hostname, "user_ip_address", [x.get("UserIPAddress") for x in interfaces])
                self.inventory.set_variable(hostname, "zone", zone)

                # add to group based on tags
                for tag in server["Tags"]:
                    if tag in skip_group_tags:
                        self.display.vvv("Skipping group for %s: %s" % (hostname, tag))
                        continue

                    self.inventory.add_group(tag)
                    self.inventory.add_child(tag, hostname)

                # constructed の compose/groups/keyed_groups を適用
                # hostvars は add_host/set_variable 済みの値を前提に評価する
                hostvars = self.inventory.get_host(hostname).get_vars()

                # compose: Jinja2 式から変数を生成
                if compose:
                    self._set_composite_vars(compose, hostvars, hostname)

                # groups: Jinja2 条件でグループに追加
                if groups:
                    self._add_host_to_composed_groups(groups, hostvars, hostname)

                # keyed_groups: 変数の値に応じてグループに追加
                if keyed_groups:
                    self._add_host_to_keyed_groups(keyed_groups, hostvars, hostname)

                # add to all group
                self.inventory.add_child("all", hostname)
