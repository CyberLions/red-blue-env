#!/usr/bin/env python3

import sys
import json

def generate_inventory(env_count):
    inventory = {
        "all": {
            "vars": {
                "ansible_ssh_private_key_file": "/home/ubuntu/red-blue-env/keys/CCDCENV.pem"
            },
            "children": {
                "windows": {"hosts": {}},
                "debian": {"hosts": {}},
                "ubuntu": {"hosts": {}},
                "centos": {"hosts": {}},
                "fedora": {"hosts": {}},
                "splunk": {"hosts": {}}
            }
        }
    }

    for i in range(1, env_count + 1):
        inventory["all"]["children"]["windows"]["hosts"][f"windows-2019-internal-{i}"] = {"ansible_host": f"10.{i}.1.10", "ansible_user": "Administrator"}
        inventory["all"]["children"]["windows"]["hosts"][f"windows-2019-user-{i}"] = {"ansible_host": f"10.{i}.2.11", "ansible_user": "Administrator"}
        inventory["all"]["children"]["debian"]["hosts"][f"debian-10-internal-{i}"] = {"ansible_host": f"10.{i}.1.11", "ansible_user": "debian"}
        inventory["all"]["children"]["ubuntu"]["hosts"][f"ubuntu-18-user-{i}"] = {"ansible_host": f"10.{i}.2.10", "ansible_user": "ubuntu"}
        inventory["all"]["children"]["ubuntu"]["hosts"][f"ubuntu-20-desktop-user-{i}"] = {"ansible_host": f"10.{i}.2.12", "ansible_user": "ubuntu"}
        inventory["all"]["children"]["splunk"]["hosts"][f"splunk-public-{i}"] = {"ansible_host": f"10.{i}.3.10", "ansible_user": "debian"}
        inventory["all"]["children"]["centos"]["hosts"][f"centos-7-public-{i}"] = {"ansible_host": f"10.{i}.3.11", "ansible_user": "centos"}
        inventory["all"]["children"]["fedora"]["hosts"][f"fedora-31-public-{i}"] = {"ansible_host": f"10.{i}.3.12", "ansible_user": "fedora"}

    return inventory

if __name__ == "__main__":
    env_count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    inventory = generate_inventory(env_count)
    print(json.dumps(inventory, indent=2))
