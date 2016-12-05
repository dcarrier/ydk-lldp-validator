![alt-text](https://developer.cisco.com/images/ydk/ydk-logo-512-(1).png)
# YDK LLDP Validator 

Manual testing cabling is error prone and time consuming. The YDK LLDP Validator assists in ensuring a data center switch is properly wired and can see all proper neighbors in a given topology.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. Please note that at this time this code is not tested for Production and is to be used for demonstration or testing purposes only. With that being said please feel free to use the code to create production ready branches!

## Prerequisities

First of all you will need the YDK libraries for Yang Model dot notation
http://ydk.cisco.com/py/docs/getting_started.html#overview

`YDK:` http://ydk.cisco.com/py/docs/getting_started.html#overview

Above will help in getting started downloading the libraries, if you would like a dev environment with YDK preinstalled:

`YDK Vagrant:` https://developer.cisco.com/site/ydk/

`XR Requirements:`You will also need a platform running XR 6.0+. 

In the running config, you should have at minimum:
```
   netconf agent tty
   lldp
```
## Installing

Once you have successfully cloned the environment you will notice three main files to utilize the YDK LLDP Validator:
##### call_lldp.py
This file imports the ```lldp_validator``` code to start the neighbor validation. It then prints the results of the validation to the tty.
##### lldp_validator.py
This is the main lldp validation code. In the LLDP validator,  ```verifylldp()``` is the main method that intializes the connection to the router/switch, kicks off the validation, and returns all results. This is the method that is called from the above file ```call_lldp.py```
##### topology.dot
The topology.dot file is the single source of truth for a given topology in a network. This file is based off of a single node and should list every interface that is receiving lldp packets.

https://en.wikipedia.org/wiki/DOT_(graph_description_language)

For example an entry of a DOT file may look like this: ```"leaf1":"Hu0/0/0/0" -- "spine4":"Hu0/0/0/0";```

In the above entry leaf1 is the node that we are validating. Leaf1 is connecting to Spine4 on local interface ```Hu0/0/0/0``` and remote interface ```Hu0/0/0/0```. The LLDP Validator always expects this format to be used. As a side note please keep in mind that the lldp_validator expects the .dot file to be named ```topology.dot``` and in the same folder as ```lldp_validator.py```

Please refer to the ```topology.dot``` file for more details!

## Example
* First I start the script: ```python call_lldp.py ssh://user:pass@ipaddress```
* Based off of the supplied ```topology.dot``` file the ```lldp_validator``` validates that the scanned node lldp neighbor information on-box matches the supplied ```topology.dot```:
```bash
  Scanned Node: leaf1
  Format: {Node : [{RECEIVED (Device Interface) : EXPECTED (Dot Interface)}]
  Everything is looking good
```

* An unsuccesful validation will show the interface that the device is connected on and what the DOT file expected:
```bash
Scanned Node: leaf1
Format: {Node : [{RECEIVED (Device Interface) : EXPECTED (Dot Interface)}]
defaultdict(<type 'list'>, {'spine3': [{'FortyGigE0/0/0/0': 'FortyGigE0/0/0/2'}]})
```

## Running the tests

To be updated with more unit tests and instructions

## To-Do's

* Update to YDK 0.5.0
* Add more unit tests and instructions

## Deployment

Not certified for production environments. To be used in test scenarios only!

## Contributing
Please feel free to fork and contribute as you see fit! Contribute.md to be added shortly!

## Authors

* **Darius Carrier**

## Acknowledgments

* ***Bruce McDougall***
* ***Santiago Alvarez***


