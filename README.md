# ipamcli - phpIPAM CLI

What is this?
-------------
With this simple phpIPAM console client you can search,add, edit or remove record for IP entry in phpIPAM manager.

Installation
------------
on most UNIX-like systems, you'll probably need to run the following
`install` commands as root or by using `sudo`

**from source**
```console
pip install git+https://github.com/verdel/ipamcli
```
**or**
```console
git clone https://github.com/verdel/ipamcli.git
cd ipamcli
python setup.py install
```

as a result, the ``ipamcli`` executable will be installed into a system ``bin``
directory

Usage
-----
Execute `ipamcli` with `--url`, `--username`, `--password`, `--vlan-list-path` options or set environment variables `IPAMCLI_URL`, `IPAMCLI_USERNAME`, `IPAMCLI_PASSWORD`, `IPAMCLI_VLAN_LIST`

With the environment variables set, running the command will look like this:

`ipamcli search --ip 192.168.1.1`

To view all the options that you can use to search for a VM, use the `--help` option:

```bash
> ipamcli --help

Usage: ipamcli [OPTIONS] COMMAND [ARGS]...

  Console utility for IPAM management with phpIPAM.

Options:
  -u, --username TEXT    Username for phpIPAM.
  -p, --password TEXT    Password for phpIPAM.
  --url TEXT             phpIPAM url.
  --vlan-list-path PATH  Path to vlan list configuration file.
  --help                 Show this message and exit.

Commands:
  add     add new entry to phpIPAM
  edit    edit exist entry in phpIPAM
  remove  remove exist entry from phpIPAM
  search  search entry in phpIPAM
  show    show entry from sub-network in phpIPAM
```

Contributing
------------

1. Check the open issues or open a new issue to start a discussion around
   your feature idea or the bug you found
2. Fork the repository and make your changes
3. Open a new pull request

If your PR has been waiting a while, feel free to [ping me on Twitter][twitter].

Use this software often? <a href="https://saythanks.io/to/valeksandrov@me.com" target="_blank"><img src="https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg" align="center" alt="Say Thanks!"></a>
:smiley:


[twitter]: http://twitter.com/verdel