import ipaddress, subprocess, uuid
from flask import request, Response, jsonify
from flask_restful import Resource
from marshmallow import ValidationError
from wgpt.models import db, Client, Server, ClientSchema, ServerSchema, Cluster, ClusterSchema, ClusterServerSchema

client_schema = ClientSchema(many=True)
server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)
cluster_server_schema = ClusterServerSchema()

def generate_server_keypair():
    p_genkey = subprocess.Popen(["wg", "genkey"], stdout=subprocess.PIPE)
    privkey = p_genkey.communicate()[0].decode().strip()

    p_pubkey = subprocess.Popen(["wg", "pubkey"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p_pubkey.stdin.write(privkey.encode("ascii"))
    pubkey = p_pubkey.communicate()[0].decode().strip()

    return privkey, pubkey

def check_ip_registered(ip):
    server = Server.query.filter_by(server_ip=ip).first()
    return server

class AddServer(Resource):
   def post(self):

        json_data = request.get_json(force=True)

        if not json_data:
            return {'status':'failure', 'message':'No input data provided'}, 400

        # load the json data into the schema and see if there's any required stuff missing
        try:
            server = server_schema.load(json_data)
        except ValidationError as err:
            return {'status':'failure', 'message':str(err.messages)}


        # Check if the server ip is already registered
        if check_ip_registered(json_data['server_ip']):
            return {'status':'failure', 'message':'server with that ip or hostname already exists'}
        else:                
            # if no keypair has been provided, generate one on the fly
            
            if json_data['server_pubkey'] is None and json_data['server_privkey'] is None:
                server_keypair = generate_server_keypair()
                server_pubkey = server_keypair[1]
                server_privkey = server_keypair[0]
            else:
                server_pubkey = json_data['server_pubkey']
                server_privkey = json_data['server_privkey']

            server_port = json_data['server_port']
            if not server_port:
                server_port = '51820'

            new_server = Server(
                server_description = json_data['server_description'],
                server_token = str(uuid.uuid4()),
                server_country = json_data['server_country'],
                server_city = json_data['server_city'],
                server_pubkey = server_pubkey,
                server_privkey = server_privkey,
                server_ip = json_data['server_ip'],
                server_port = server_port,
                server_networkv4 = json_data['server_networkv4'],
                server_networkv6 = json_data['server_networkv6'],
                server_dns = json_data['server_dns'],
                server_postup = json_data['server_postup'],
                server_postdown = json_data['server_postdown'],
                cluster_id = json_data['cluster_id'],
                server_persistentkeepalive = json_data['server_persistentkeepalive'],
                server_ssh_key = None,
            )

        # Add server to db
        db.session.add(new_server)
        db.session.commit()
        server = server_schema.dump(new_server)
        return {'status':'success', 'data': server}

class AddServerToCluster(Resource):
    def post(self, cluster_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status':'failure', 'message':'No input data provided'}, 400

        # load the json data into the schema and see if there's any required stuff missing
        try:
            cluster_server = cluster_server_schema.load(json_data)
        except ValidationError as err:
            return {'status':'failure', 'message':str(err.messages)}
    

        # Check if the server ip is already registered
        if check_ip_registered(json_data['server_ip']):
            return {'status':'failure', 'message':'server with that ip or hostname already exists'}

        new_server = Server(
            server_ip = json_data['server_ip'],
            cluster_id = cluster_id,
            server_pubkey = None,
            server_privkey = None, 
            server_networkv4 = None,
            server_networkv6 = None,
            server_port = None,
            server_dns = None,
            server_city = json_data['server_city'],
            server_country = json_data['server_country'],
            server_postup = None,
            server_postdown = None, 
            server_token = str(uuid.uuid4()),
            server_persistentkeepalive = None,
            server_description = json_data['server_description'],
            server_ssh_key = None
        )
    
        db.session.add(new_server)
        db.session.commit()
        server = server_schema.dump(new_server)
        return {'status':'success', 'data':server}

class UpdateServer(Resource):
    def post(self, server_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status':'failure', 'message':'No input data provided'}, 400

        server = Server.query.filter_by(id=json_data['id']).first()
        if not server:
            return {'status':'failure', 'message':'No server by that id'}, 400

        server.server_description = json_data['server_description']
        server.server_country = json_data['server_country']
        server.server_city = json_data['server_city']
        server.server_postup = json_data['server_postup']
        server.server_postdown = json_data['server_postdown']

        db.session.commit()
        return {'status':'success', 'data':server_schema.dump(server)}


class UpdateServerToCluster(Resource):
    def post(self, server_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status':'failure', 'message':'No input data provided'}, 400

        server = Server.query.filter_by(id=json_data['id']).first()
        if not server:
            return {'status':'failure', 'message':'No server by that id'}, 400

        server.server_description = json_data['server_description']
        server.server_country = json_data['server_country']
        server.server_city = json_data['server_city']

        db.session.commit()
        return {'status':'success', 'data':server_schema.dump(server)}


class DeleteServer(Resource):
    def delete(self, server_id):
        if server_id:
            server = Server.query.filter_by(id=server_id).first()
        if server:
            db.session.delete(server)
            db.session.commit()
            return { 'status' : 'success', 'data' : {'server_id': str(server_id)} }, 200
        else:
            return { 'status' : 'failure', 'message' : 'Server with ' + str(server_id) + ' not found'}

class GetServers(Resource):
    def get(self):
        servers = Server.query.filter_by(cluster_id=None).all()
        servers = servers_schema.dump(servers)
        return {'status':'success', 'data':servers}, 200

class GetServer(Resource):
    def get(self, server_id):
        server = Server.query.filter_by(id=server_id).first()
        if server:
            if server.cluster_id is None:
                clients = Client.query.filter_by(server_id=server_id).count()
                network = int(server.server_networkv4.split('/')[1])
                network_clients = (2**(32-network)-2)
                server = server_schema.dump(server)
                return {'status':'success', 'data':server, 'capacity':{'total':network_clients, 'available':network_clients-clients, 'in use':clients}}, 200
            else:
                server = server_schema.dump(server)
                return {'status':'success', 'data':server}, 200
        else:
            return {'status':'failure', 'message':'No server with that id found'}

class GetServersByClusterId(Resource):
    def get(self, cluster_id):
        servers = Server.query.filter_by(cluster_id=cluster_id).all()
        if servers:
            servers = servers_schema.dump(servers)
            return {'status':'success', 'data':servers}, 200
        else:
            return {'status':'failure', 'message':'No cluster with that id found'}, 200

class GetServerConfig(Resource):
    def get(self, server_id):
        server = Server.query.filter_by(id=server_id).first()        
        if server is None:
            return {'status':'failure', 'message':'No server with that id found'}
        if server.cluster_id:
            return {'status':'failure', 'message':'this server is part a cluster, use /api/clusters/get/config/<int:cluster_id> instead'}

        clients = Client.query.filter_by(server_id=server_id).all()
        config=''
        config += '[Interface]\n'
        if server.server_networkv4 and server.server_networkv6:
            config += 'Address = ' + server.server_networkv4 + ', ' + server.server_networkv6 +'\n'
        if server.server_networkv4 and not server.server_networkv6:
            config += 'Address = ' + server.server_networkv4 +'\n'
        if server.server_networkv6 and not server.server_networkv4:
            config += 'Address = ' + server.server_networkv6 +'\n'
        config += 'PrivateKey = ' + server.server_privkey +'\n'
        config += 'ListenPort = ' + str(server.server_port) +'\n'
        if server.server_postup:
            config += 'PostUp = ' + str(server.server_postup) +'\n'
        if server.server_postdown:
            config += 'PostDown = ' + str(server.server_postdown) +'\n'
        config += '\n'

        for client in clients:
            config += '[Peer]\n'
            config += 'PublicKey = ' + client.client_pubkey + '\n'
            if client.client_ipv4 and client.client_ipv6:
                config += 'AllowedIPs = ' + client.client_ipv4 + ',' + client.client_ipv6 + '\n'
            if client.client_ipv4 and not client.client_ipv6:
                config += 'AllowedIPs = ' + client.client_ipv4 + '\n'
            if not client.client_ipv4 and client.client_ipv6:
                config += 'AllowedIPs = ' + client.client_ipv6 + '\n'
            config += '\n'

        return Response(config, mimetype='text')


class GetServerConfigJson(Resource):
    def get(self, server_id):
        server = Server.query.filter_by(id=server_id).first()
        
        if server is None:
            return {'status':'failure', 'message':'No server with that id found'}
        
        if server.cluster_id:
            return {'status':'failure', 'message':'this server is part of a cluster, use /api/clusters/get/config/<int:cluster_id>'}
            
        clients = server.clients
        server = server_schema.dump(server)
        clients = client_schema.dump(clients)
        return {'status':'success', 'data':{'server':server, 'clients':clients}}
