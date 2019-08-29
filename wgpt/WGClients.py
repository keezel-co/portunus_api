import ipaddress, subprocess
from flask import request, Response
from flask_restful import Resource
from wgpt.models import db, Client, Server, Cluster, ClientSchema, ServerSchema, ClusterSchema
from wgpt.wg_ssh_update import send_ssh_command

clients_schema = ClientSchema(many=True)
client_schema = ClientSchema()


def generate_client_keypair():
    p_genkey = subprocess.Popen(["wg", "genkey"], stdout=subprocess.PIPE)
    privkey = p_genkey.communicate()[0].decode().strip()

    p_pubkey = subprocess.Popen(["wg", "pubkey"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p_pubkey.stdin.write(privkey.encode("ascii"))
    pubkey = p_pubkey.communicate()[0].decode().strip()

    return privkey, pubkey

def get_next_availabe_ip(network, client_ips):
    hosts_iterator = (host for host in network if host not in client_ips)
    try:
        client_ip = str(next(hosts_iterator))
        return client_ip
    except:
        return False
    

class AddClientToServer(Resource):
    def post(self, server_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message':'No input data provided'}, 400
        
        server = Server.query.filter_by(id=server_id).first()

        if not server:
            return {'status':'failure', 'message':'Server not found'}
        
        # Fetch client information for server to obtain free IP addresses
        clients = Client.query.filter_by(server_id=json_data['server_id'])

        client_ipv4 = None
        client_ipv6 = None
        if server.server_networkv4:
            server_networkv4 = ipaddress.ip_network(server.server_networkv4).hosts()
            clients_ipv4 = []
            for client in clients:
                clients_ipv4.append(ipaddress.ip_address(client.client_ipv4))
            client_ipv4 = get_next_availabe_ip(server_networkv4, clients_ipv4)
        
        if server.server_networkv6:
            server_networkv6 = ipaddress.ip_network(server.server_networkv6).hosts()
            clients_ipv6 = []
            for client in clients:
               clients_ipv6.append(ipaddress.ip_address(client.client_ipv6))
            client_ipv6 = get_next_availabe_ip(server_networkv6, clients_ipv6)        
    
         
        # Generate keys
        if client_ipv4 or client_ipv6:
            client_keypair = generate_client_keypair()
            client_privkey = client_keypair[0]
            client_pubkey = client_keypair[1]
        else:
            return {'status':'failure','message':'Could not assign IP to client. Network full?'}

        
        # Create the client through SSH on server if configured
        if server.server_ssh_key:
            if client_ipv4:
                ssh_success = send_ssh_command('add', server.server_ip + ' ' + server.server_ssh_key, client_pubkey, client_ipv4)
                if not ssh_success:
                    return {'status':'failure', 'message':'There was a problem with the ssh provisioning.'}
            if client_ipv6: 
                ssh_success = send_ssh_command('add', server.server_ip + ' ' + server.server_ssh_key, client_pubkey, client_ipv6)
                if not ssh_success:
                    return {'status':'failure', 'message':'There was a problem with the ssh provisioning.'}


        # Store the client information in the database
        new_client = Client(
                client_ipv4 = client_ipv4,
                client_ipv6 = client_ipv6,
                client_pubkey = client_pubkey,
                server_id = json_data['server_id'],
                cluster_id = None,
                client_description = json_data['client_description']
            )
        db.session.add(new_client)
        db.session.commit()

        data= {}
        data['client_id'] = new_client.id
        data['client_ipv4'] = client_ipv4
        data['client_ipv6'] = client_ipv6
        data['client_pubkey'] = client_pubkey
        data['client_privkey'] = client_privkey
        data['server_ip'] = server.server_ip
        data['server_port'] = server.server_port
        data['server_pubkey'] = server.server_pubkey
        if server.server_dns is not None:
            data['server_dns'] = server.server_dns
        data['server_id'] = json_data['server_id']

        return {'status': 'success', 'data': data}                    


class AddClientToCluster(Resource):
    def post(self, cluster_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message':'No input data provided'}, 400

        cluster = Cluster.query.filter_by(id=cluster_id).first()

        if not cluster:
            return {'status':'failure', 'message':'Cluster not found'}

        # Get relevant server data
                
        # Get occupied client ip addresses on server
        clients = Client.query.filter_by(cluster_id=cluster_id)

        client_ipv4 = None
        client_ipv6 = None
        if cluster.cluster_networkv4:
            cluster_networkv4 = ipaddress.ip_network(cluster.cluster_networkv4).hosts()
            clients_ipv4 = []
            for client in clients:
                clients_ipv4.append(ipaddress.ip_address(client.client_ipv4))
            client_ipv4 = get_next_availabe_ip(cluster_networkv4, clients_ipv4)
        
        if cluster.cluster_networkv6:
            cluster_networkv6 = ipaddress.ip_network(cluster.cluster_networkv6).hosts()
            clients_ipv6 = []
            for client in clients:
               clients_ipv6.append(ipaddress.ip_address(client.client_ipv6))
            client_ipv6 = get_next_availabe_ip(cluster_networkv6, clients_ipv6)    

        # Generate keys
        if client_ipv4 or client_ipv6:
            client_keypair = generate_client_keypair()
            client_privkey = client_keypair[0]
            client_pubkey = client_keypair[1]
        else:
            return {'status':'failure','message':'Could not assign IP to client. Network full?'}
            
        # Store the client information in the database
        new_client = Client(
                client_ipv4 = client_ipv4,
                client_ipv6 = client_ipv6,
                client_description = json_data['client_description'],
                client_pubkey = client_pubkey,
                cluster_id = json_data['cluster_id'],
                server_id  = None,
            )
        db.session.add(new_client)
        db.session.commit()

        return {'status': 'success', 'data': {
            'client_id': new_client.id,
            'client_ipv4': client_ipv4,
            'client_ipv6': client_ipv6,
            'client_pubkey': client_pubkey,
            'client_privkey': client_privkey,
            'cluster_pubkey': cluster.cluster_pubkey,
            'cluster_dns': cluster.cluster_dns,
            'cluster_id': cluster.id
            }
        }


class GetClient(Resource):
    def get(self, client_id):
        clients = Client.query.filter_by(id=client_id).first()
        if not clients:
            return {'status':'failure', 'message':'No client with that id found'}, 200    
        clients = client_schema.dump(clients)
        return {'status':'success', 'data':clients}, 200

class GetClients(Resource):
    def get(self):
        clients = Client.query.all()
        clients = clients_schema.dump(clients)
        return {'status':'success', 'data':clients}, 200

class GetClientsByServerId(Resource):
    def get(self, server_id):
        clients = Client.query.filter_by(server_id=server_id).all()
        if not clients:
            return {'status':'failure', 'message':'no clients found for that server id'}
        clients = clients_schema.dump(clients)
        return {'status':'success', 'data':clients}, 200
        
            
class GetClientsByClusterId(Resource):
    def get(self, cluster_id):
        clients = Client.query.filter_by(cluster_id=cluster_id).all()
        if not clients:
            return {'status':'failure', 'message':'no clients found for that cluster id'}
        clients = clients_schema.dump(clients)
        return {'status':'success', 'data':clients}, 200

class DeleteClient(Resource):
    def delete(self, client_id):
        if client_id:
            client = Client.query.filter_by(id=client_id).first()
            if not client:
                return {'status':'failure', 'message':'no clients found for that id'}
            
            server = Server.query.filter_by(id=client.server_id).first()

            # Create the client through SSH on server if configured
            if server.server_ssh_key:
                if client.client_ipv4:
                    ssh_success = send_ssh_command('remove', server.server_ip + ' ' + server.server_ssh_key, client.client_pubkey, client.client_ipv4)
                    if not ssh_success:
                        return {'status':'failure', 'message':'There was a problem with the ssh provisioning.'}
                if client.client_ipv6: 
                    ssh_success = send_ssh_command('remove', server.server_ip + ' ' + server.server_ssh_key, client.client_pubkey, client.client_ipv6)
                    if not ssh_success:
                        return {'status':'failure', 'message':'There was a problem with the ssh provisioning.'}


            
            
            db.session.delete(client)
            db.session.commit()
            return { 'status' : 'success', 'data':{'client_id':client_id}}, 200
            
            




