# Role Name
joe-speedboat.fact_inventory


## Description
This Ansible role allows you to gather essential facts from various endpoint resources, providing valuable information for managing your infrastructure. Whether you need to deploy virtual machines, create an overview of your resources, or visualize network topologies, this role simplifies the process by collecting facts from different endpoints.


## Features
- **Resource Agnostic**: Works with a variety of endpoint resources, such as VMware vCenter, AWS, Azure, and more.
- **Easy Configuration**: Simple configuration using YAML variables to specify the resources you want to gather facts from.
- **Structured Data**: Collects structured data, including data centers, clusters, hosts, virtual machines, datastores, networks, and more.
- **JSON Output**: Generates a well-formatted JSON file with the gathered facts, suitable for further analysis or visualization.


## Requirements
- Ansible >= 2.11
- Python >= 3.6 (on the target host)
- Python packages:
  - pip
  - setuptools
  - [vsphere-automation-sdk-python](https://github.com/vmware/vsphere-automation-sdk-python)
- Ansible collection:
  - community.vmware


## Role Variables
The following variables are available for configuration:

- `inventory_file`: The path to the inventory file. Default is `/tmp/fact_inventory.json`.
- `debug_vars`: A boolean to toggle debug mode. Default is `True`.
- `inventory_targets`: A list of targets to gather facts from. Each target should be a dictionary with the following keys:
  - `ressource_name`: The name of the resource.
  - `type`: The type of the resource (e.g., "vsphere").
  - `validate_certs`: A boolean to toggle certificate validation.
  - `vcenter_api_url`: The URL of the vCenter API.
  - `vcenter_username`: The username for the vCenter API.
  - `vcenter_password`: The password for the vCenter API.
  - `datacenter_regex`: A regular expression to filter the data centers.
  - `cluster_regex`: A regular expression to filter the clusters.
  - `host_regex`: A regular expression to filter the hosts.
  - `datastore_regex`: A regular expression to filter the datastores.
  - `network_regex`: A regular expression to filter the networks.
  - `vm_folder_regex`: A regular expression to filter the VM folders.


## Dependencies
None.


## License
GPLv3


## Usage
To use this role, you need to specify the variables in the `inventory_targets` list in your playbook or in the `defaults/main.yml` file. Each item in the list represents a target from which to gather facts. 

The `datacenter_regex`, `cluster_regex`, `host_regex`, `datastore_regex`, `network_regex` and `vm_folder_regex` variables allow you to filter the results from the vSphere API. These variables accept regular expressions. For example, if you want to gather facts only from data centers whose names start with "dc", you can set `datacenter_regex` to '^dc'.

## Testing
Before running the tests, you need to create a `vars.yml` file in the `tests` directory with your specific configuration. You can do this by copying the `vars_example.yml` file:

```bash
cp tests/vars_example.yml tests/vars.yml
```

Then, fill the `vars.yml` file with your specific values, including the regular expressions for filtering.

To run the tests, execute the following command:

```bash
ansible-playbook tests/test.yml -i tests/inventory
```

This command will run the playbook `test.yml` using the inventory file located in the `tests` directory.


## CGI Script for Rundeck Options
With Rundeck and JSON, you can create great job menus.   
But for that you need to setup cgi server first and use it with json resource file, created by this role.   
Here is how to setup `lighttpd` with cgi on Rocky Linux 8
```bash
dnf install lighttpd
systemctl enable lighttpd

cp -av /etc/lighttpd/modules.conf /etc/lighttpd/modules.conf.orig
cp -av /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.orig
cp -av /etc/lighttpd/conf.d/cgi.conf /etc/lighttpd/conf.d/cgi.conf.orig

sed -i 's@.*\(include.*conf.d/cgi.conf"\).*@\1@' /etc/lighttpd/modules.conf
sed -i 's@.*server\.use-ipv6.*@server\.use-ipv6 = "disable"@' /etc/lighttpd/lighttpd.conf
sed -i 's@.*server\.bind.*@server\.bind = "localhost"@' /etc/lighttpd/lighttpd.conf
sed -i 's@.*server\.port.*@server\.port = 8888@' /etc/lighttpd/lighttpd.conf
semanage port -a -t http_port_t -p tcp 8888
systemctl restart lighttpd
systemctl status lighttpd

lsof -i -P -n | grep light

test -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

mkdir -p /var/www/lighttpd/cgi-bin

vi /var/www/lighttpd/cgi-bin/test.cgi
------------------
#!/usr/bin/env python3

print("Content-Type: text/html")  # HTML is following
print()  # blank line, end of headers
print("<html>")
print("<head><title>Hello CGI</title></head>")
print("<body>")
print("<h1>Hello World</h1>")
print("</body>")
print("</html>")
----------------------
chmod +x /var/www/lighttpd/cgi-bin/test.cgi

curl http://127.0.0.1:8888/cgi-bin/test.cgi
```

In this roles, i provided a cgi which could be used to serve this options, its in `tests/cgi-bin/option.py` just copy it to cgi-bin dir, update json file location and call it.   
Please keep in mind, that this cgi is just a proof of concept at the moment, quick and dirty

```
cp tests/cgi-bin/option.py /var/www/lighttpd/cgi-bin/option.cgi
chmod +x /var/www/lighttpd/cgi-bin/option.cgi
vi /var/www/lighttpd/cgi-bin/option.cgi # update json file location
```

And then you can call it within rundeck:
* http://127.0.0.1:8888/cgi-bin/option.py?filter=type:vsphere&filter=type:datacenter&key=name
```
[ "Datacenter1" ]
```
* http://127.0.0.1:8888/cgi-bin/option.py?filter=type:vsphere&filter=type:datacenter,name:${option.DataCenter.value}&filter=type:cluster&key=name
```
[ "Cluster1" ]

```
* http://127.0.0.1:8888/cgi-bin/option.py?filter=type:vsphere&filter=type:datacenter,name:${option.DataCenter.value}&filter=type:cluster,name:${option.Cluster.value}&filter=type:datastore&key=name
```
[ "LUN_01_VM_Replica", "LUN_02_VM_Replicas" ]
```
And this is quite amazing ... with not much effort
