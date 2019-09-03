# Portunus

Portunus is a set of tools that make it easy to deploy and manage Wireguard
servers and clients at scale. The portunus_api allows you to create
servers, assign address ranges and then dynamically assign addresses from that
range to clients. It can output data in JSON as well as Wireguard configuration
file format and allows working with 'clusters' (groups of servers that share the
same clients). 

Check out the video here: https://youtu.be/2ERNDbl1VAM

# portunus_api

`portunus_api` contains the API, database and rudamentary web interface. You 
can use this stand-alone and implement further dissemination of the 
configurations through your network yourself. Or you can use the rest of
the tools to provision automatically, see below for more information on that.

# Installation
Ensure you have `docker` and `docker-composer` installed on your system.
1. `git clone https://gitlab.keezel.nl/wgpt/portunus_api/`
2. `cd portunus_api && docker-compose up --build`

Access the web interface / api through:
`https://yourserver.com:1443/web/index.html`
Default login: admin/password

# More information on the API, how to set up full provisioning, etc check out:
See the documentation repository: https://github.com/keezel-co/portunus_documentation
