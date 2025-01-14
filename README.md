# CCSO K8s OpenStack Deployment
This Ansible playbook installs Kubernetes and then installs OpenStack on top of Kubernetes.

## What is Ansible?
Ansible is somewhat similar to bash scripting, except that it is designed to connect to orchestrate and deploy large environments idempotently. A good, quick overview is available on [RedHat's Website](https://www.redhat.com/en/blog/ansible-101-ansible-beginners). For a more extensive overview, Jeff Geerling has a good series on his [website](https://www.jeffgeerling.com/blog/2020/ansible-101-jeff-geerling-youtube-streaming-series).

### What is Idempotency?
From Google:
>An API call or operation is idempotent if it has the same result no matter how many times it's applied. That is, an idempotent operation provides protection against accidental duplicate calls causing unintended consequences.

In our case, this means that if we want to apply a change to a system, regardless the number of the times that we run our playbook/script, it will result in the same outcome.

For example, the following bash script to add a line to a configuration file is not idempotent:
```
echo "IncludeOptional conf-enabled/*.conf" >> /etc/apache2/apache2.conf
```
If this is re-run, it will result in `IncludeOptional conf-enabled/*.conf` being added to the configuration file again.

However, in Ansible, we can use the following to add that line to the config file idempotently:
```
- name: Replace a localhost entry searching for a literal string to avoid escaping
  ansible.builtin.lineinfile:
    path: /etc/apache2/apache2.conf
    line: "IncludeOptional conf-enabled/*.conf"
```
Yes, we could write a bash script to do that. However, the human readable and thoroughly tested Ansible modules allow us to write more code quicker than in bash or other scripting languages.

## Getting Started
The following steps will get you up and running:
1. Create a VENV: `python3 -m venv venv`
2. Activate the VENV: `source venv/bin/activate`
3. Install Ansible and depends: `python3 -m pip install -r requirements.txt`
4. Install Ansible Galaxy Packages: `ansible-galaxy install -r requirements.yml`
Please note that you will need to rerun `source venv/bin/activate` before using the playbook. When you are done using the playbook you can close the VENV by using the `deactivate` command.

## Building the ISO:
The ISO will be built on your local machine. To build the base ISO, use the following commands:
1. Run the playbook: `ansible-playbook playbooks/iso.yaml`
2. Check the ISO folder added to the root of the project for the outputted ISO.
3. When satisfied, delete the ISO folder to free up space. Do __NOT__ commit the ISO folder to the git repo (it is too large).

## Running the Deployment Playbook
The following commands will run the deployment playbook. Prior to running this playbook, install the customized ISO on at least one node.
### Deploy PXE Boot Server
Add the pxeboot node to the inventory.
#### Example:
```
all:
  hosts:
    s1:
      ansible_host: 10.0.101.11
      ip: 10.0.101.11
...
  children:
    pxe_boot:
      hosts:
        s1:
```

Run the playbook with the pxeboot tag:
```
ansible-playbook deploy.yaml -i inventories/rack/hosts --become --ask-become-pass --ask-vault-pass --ask-pass --tags pxeboot
```
After running this, see the [pxeboot role's readme](roles/00-pxe-boot/README.md) for instructions on configuring the router. After that, you can begin PXE booting nodes.

## Deploying Everything
Before deploying everything, ensure that the nodes are PXE booted and DHCP leases are properly set. Then, you can run the entire playbook with `ansible-playbook deploy.yaml -i inventories/rack/hosts --become --ask-become-pass --ask-vault-pass --ask-pass`.

## GitHub Actions Power Control
> [!WARNING]  
> The servers will not instantly start and stop. Please allow 30 minutes between start and stop operations. Failure to do so may result in an inconsistent power state.

You can control the power state of the rack through GitHub actions.
![Power control steps](./docs/resources/gh_power_control.png)

## Manually Startup Cluster
> [!NOTE]  
> It will take some time for all of the services on the rack to be online and ready. The playbook only waits for the nodes to respond to SSH.

To start up all of the servers on the cluster, run the following command: `ansible-playbook playbooks/startup.yaml -i inventories/rack/hosts --become --ask-become-pass --ask-vault-pass --ask-pass`. This will use the Cisco IMC to start up the servers. Then, it will wait for all servers to complete booting and have SSH access. This may take a minute or two to complete.

## Manually Shutdown Cluster
To shutdown the cluster, run `ansible-playbook playbooks/shutdown.yaml -i inventories/rack/hosts --become --ask-become-pass --ask-vault-pass --ask-pass`. This will connect to each of the nodes in the inventory and shut down the servers.

## Rook (Ceph) Resources
[Rook](https://rook.io/) is a management platform for Ceph. Ceph provides distributed and failure tolerant storage across all of the servers in the rack. 

### Access the Ceph Dashboard
The Ceph dashboard is accessible at [rook.rack.psuccso.org](http://rook.rack.psuccso.org/) from within the rack network. The username is `admin`. The password can be found using the following command: `kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o jsonpath="{['data']['password']}" | base64 --decode && echo`.

## Openstack Resources
The following resources are a good place to get started with Openstack. This stack is deployed on top of Kubernetes using [Openstack-helm](https://docs.openstack.org/openstack-helm/latest/).
### Openstack CLI:
> [!TIP]
> Openstack CLI interacts directly with the Openstack microservice API endpoints. The public domain for each microservice must be mapped to the ingress load balancer IP.

The Openstack CLI provides a CLI interface to interact with the Openstack micro services. Unlike the web interface, Horizon, the CLI tools directly interact with the Openstack micro-services. To install the CLI, please refer to the instructions on [OpenMetal.io's website](https://openmetal.io/docs/manuals/operators-manual/day-1/command-line/openstackclient) or the [Openstack Wiki](https://docs.openstack.org/newton/user-guide/common/cli-install-openstack-command-line-clients.html).
### Images:
Images are stored in Glance, an image repository. You can find images at the following sites:
- [Openstack Documentation](https://docs.openstack.org/image-guide/obtain-images.html)
- [Bigstack](https://docs.bigstack.co/docs/downloads/cloud_image)
- [Kali](https://www.kali.org/get-kali/#kali-cloud)

While you can upload ISOs to Glance, it is not suggested. Cloud images can be configured with [cloud-init](https://cloudinit.readthedocs.io/). Cloud images are significantly quicker to install and get running when compared to an ISO installation.
#### Using ISOs:
> [!IMPORTANT]
> Using ISO images to create VMs is not preferred. Use cloud images whenever possible.

You can create VMs using ISO images, see the guide on [OpenMetal.io's website](https://openmetal.io/docs/manuals/tutorials/understanding-iso-images) for instructions.

#### Uploading Images CLI
Use the following command to upload images via the OpenStack CLI:
```bash
openstack image create \
--disk-format <DISK FORMAT> \
--container-format bare \
--public \
--project "<PROJECT NAME>" \
--file <FILE> \
--min-disk <DISK MIN GB> \
--min-ram <RAM MIN MB> \
--progress \
"<NAME OF IMAGE>"
```
Example using the Windows 10 Image from Bigstack:
```bash
openstack image create \
--disk-format vmdk \
--container-format bare \
--public \
--file ./win10en-230505.vmdk \
--min-disk 20 \
--min-ram 4096 \
--progress \
"Windows 10 230505"
```
For more information on the CLI args, see the [OpenStack Docs](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/image-v2.html).
