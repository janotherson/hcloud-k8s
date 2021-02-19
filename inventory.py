#!/usr/bin/env python3
import json
import subprocess


def get_terraform_output():
    return json.loads(
        subprocess.check_output(["terraform", "output", "-json"]).decode("utf-8")
    )


def build_inventory(terraform_output):
    inventory = {
        "_meta": {
            "hostvars": {},
        },
        "all": {
            "children": ["node"],
        },
        "node": {
            "children": ["controlnode", "workernode"],
            "vars": {},
        },
        "controlnode": {
            "hosts": [],
        },
        "workernode": {
            "hosts": [],
        },
    }

    terraform_output = get_terraform_output()

    # fmt: off
    inventory["node"]["vars"]["k8s_hcloud_token"] = \
        terraform_output["hcloud_token"]["value"]

    inventory["node"]["vars"]["k8s_cluster_name"] = \
        terraform_output["cluster_name"]["value"]

    inventory["node"]["vars"]["k8s_ip_range_service"] = \
        terraform_output["cluster_network_ip_range_service"]["value"]

    inventory["node"]["vars"]["k8s_ip_range_pod"] = \
        terraform_output["cluster_network_ip_range_pod"]["value"]

    inventory["node"]["vars"]["k8s_control_plane_endpoint"] = \
        terraform_output["controllb_private_k8s_endpoint"]["value"]

    inventory["node"]["vars"]["k8s_apiserver_cert_extra_sans"] = \
        [terraform_output["controllb_ipv4_address"]["value"]]

    inventory["node"]["vars"]["k8s_ingress"] = \
        terraform_output["cluster_ingress"]["value"]

    inventory["node"]["vars"]["k8s_cni"] = \
        terraform_output["cluster_cni"]["value"]
    # fmt: on

    for group in [
        [
            terraform_output["controlnode_names"]["value"],
            terraform_output["controlnode_ipv4_addresses"]["value"],
            "controlnode",
        ],
        [
            terraform_output["workernode_names"]["value"],
            terraform_output["workernode_ipv4_addresses"]["value"],
            "workernode",
        ],
    ]:
        for node in range(len(group[0])):
            node_name = group[0][node]
            node_ipv4_address = group[1][node]
            node_group = group[2]

            inventory["_meta"]["hostvars"][node_name] = {
                "ansible_host": node_ipv4_address,
            }
            inventory[node_group]["hosts"].append(node_name)

    return inventory


if __name__ == "__main__":
    print(json.dumps(build_inventory(get_terraform_output())))
