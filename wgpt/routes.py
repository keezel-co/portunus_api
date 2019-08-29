from flask import Blueprint, send_from_directory
from flask_restful import Api
from wgpt import app, db, api

from wgpt.WGClients import *
from wgpt.WGServers import *
from wgpt.WGClusters import *


# Static
@app.route('/web/<path:path>')
def send_static(path):
    return send_from_directory('web', path)

# Clients
api.add_resource(GetClient, '/api/clients/get/<int:client_id>')
api.add_resource(GetClients, '/api/clients/get/all')
api.add_resource(GetClientsByServerId, '/api/clients/get/by_server_id/<int:server_id>')
api.add_resource(GetClientsByClusterId, '/api/clients/get/by_cluster_id/<int:cluster_id>')
api.add_resource(AddClientToServer, '/api/clients/add_to_server/<int:server_id>')
api.add_resource(AddClientToCluster, '/api/clients/add_to_cluster/<int:cluster_id>')
api.add_resource(DeleteClient, '/api/clients/delete/<int:client_id>')

# Servers
api.add_resource(GetServer, '/api/servers/get/<int:server_id>')
api.add_resource(GetServers, '/api/servers/get/all')
api.add_resource(GetServersByClusterId, '/api/servers/get/by_cluster_id/<int:cluster_id>')
api.add_resource(GetServerConfig, '/api/servers/get/config/<int:server_id>')
api.add_resource(GetServerConfigJson, '/api/servers/get/config/json/<int:server_id>')
api.add_resource(AddServer, '/api/servers/add')
api.add_resource(AddServerToCluster, '/api/servers/add_to_cluster/<int:cluster_id>')
api.add_resource(UpdateServerToCluster, '/api/servers/update_to_cluster/<int:server_id>')
api.add_resource(UpdateServer, '/api/servers/update/<int:server_id>')
api.add_resource(DeleteServer, '/api/servers/delete/<int:server_id>')

# Clusters

api.add_resource(GetCluster, '/api/clusters/get/<int:cluster_id>')
api.add_resource(GetClusters, '/api/clusters/get/all')
api.add_resource(GetClusterConfig, '/api/clusters/get/config/<int:cluster_id>')
api.add_resource(AddCluster, '/api/clusters/add')
api.add_resource(UpdateCluster, '/api/clusters/update/<int:cluster_id>')
api.add_resource(DeleteCluster, '/api/clusters/delete/<int:cluster_id>')

api.init_app(app)