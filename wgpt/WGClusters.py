import ipaddress, subprocess
from flask import request, Response
from flask_restful import Resource
from marshmallow import Schema, fields, pre_load, validate, ValidationError
from wgpt.models import db, Client, Server, Cluster, ClientSchema, ServerSchema, ClusterSchema

client_schema = ClientSchema()
server_schema = ServerSchema()
cluster_schema = ClusterSchema()
clusters_schema = ClusterSchema(many=True)

def generate_server_keypair():
    p_genkey = subprocess.Popen(["wg", "genkey"], stdout=subprocess.PIPE)
    privkey = p_genkey.communicate()[0].decode().strip()

    p_pubkey = subprocess.Popen(["wg", "pubkey"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p_pubkey.stdin.write(privkey.encode("ascii"))
    pubkey = p_pubkey.communicate()[0].decode().strip()

    return privkey, pubkey

class GetCluster(Resource):
    def get(self, cluster_id):
        cluster = Cluster.query.filter_by(id=cluster_id).first()
        if not cluster:
            return {'status':'failure', 'message':'no cluster found for that id'}
        cluster = cluster_schema.dump(cluster)
        return {'status':'success', 'data':cluster}, 200

class GetClusters(Resource):
    def get(self):
        clusters = Cluster.query.all()
        clusters = clusters_schema.dump(clusters)
        return {'status':'success', 'data':clusters}, 200

class DeleteCluster(Resource):
    def delete(self, cluster_id):
        cluster = Cluster.query.filter_by(id=cluster_id).first()
        if not cluster:
            return {'status':'failure', 'message':'no cluster found for that id'}
        db.session.delete(cluster)
        db.session.commit()
        return { 'status':'succes', 'data':{'cluster_id':str(cluster_id)}}, 200

class UpdateCluster(Resource):
    def post(self, cluster_id):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status':'failure', 'message':'No input data provided'}, 400

        cluster = Cluster.query.filter_by(id=cluster_id).first()
        if not cluster:
            return {'status':'failure', 'message':'No cluster with that id found'}, 400

        cluster.cluster_description = json_data['cluster_description']
        cluster.cluster_postup = json_data['cluster_postup']
        cluster.cluster_postdown = json_data['cluster_postdown']

        db.session.commit()

        return {'status':'success', 'data': cluster_schema.dump(cluster)}

class AddCluster(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message':'No input data provided'}, 400

        # load the json into the schema and check if required things are missing
        try:
            cluster = cluster_schema.load(json_data)    
        except ValidationError as err:
            return {'status':'failure', 'message':str(err.messages)}
        
        if cluster['cluster_pubkey'] is None and cluster['cluster_privkey'] is None:
            cluster_keypair = generate_server_keypair()
            cluster['cluster_pubkey'] = cluster_keypair[1]
            cluster['cluster_privkey'] = cluster_keypair[0]
        
        cluster_port = json_data['cluster_port']
        if not cluster_port:
            cluster_port = '51820'

        new_cluster = Cluster(
            cluster_description = cluster['cluster_description'],
            cluster_port =  cluster_port,
            cluster_dns = cluster['cluster_dns'],
            cluster_pubkey =  cluster['cluster_pubkey'],
            cluster_privkey = cluster['cluster_privkey'],
            cluster_networkv4 = cluster['cluster_networkv4'],
            cluster_networkv6 = cluster['cluster_networkv6'],
            cluster_postup = cluster['cluster_postup'],
            cluster_postdown = cluster['cluster_postdown'],
            cluster_persistentkeepalive = cluster['cluster_persistentkeepalive']
            )

        db.session.add(new_cluster)
        db.session.commit()

        return {'status':'success', 'data':cluster_schema.dump(new_cluster)}
    

class GetClusterConfig(Resource):
    def get(self, cluster_id):
        cluster = Cluster.query.filter_by(id=cluster_id).first()
        if not cluster:
            return {'status':'failure', 'message':'no cluster by that id'}

        clients = cluster.clients
        config=''
        config += '[Interface]\n'
        if cluster.cluster_networkv4 and cluster.cluster_networkv6:
            config += 'Address = ' + cluster.cluster_networkv4 + ', ' + cluster.cluster_networkv6 + '\n'
        if cluster.cluster_networkv4 and not cluster.cluster_networkv6:
            config += 'Address = ' + cluster.cluster_networkv4 + '\n'
        if cluster.cluster_networkv6 and not cluster.cluster_networkv4:
            config += 'Address = ' + cluster.cluster_networkv6 + '\n'
        config += 'PrivateKey = ' + cluster.cluster_privkey +'\n'
        config += 'ListenPort = ' + str(cluster.cluster_port) +'\n'
        config += '\n'

        for client in clients:
            config += '[Peer]\n'
            config += 'PublicKey = ' + client.client_pubkey + '\n'
            if client.client_ipv4 and client.client_ipv6:
                config += 'AllowedIPs = ' + client.client_ipv4 + ',' + client.client_ipv6 + '\n'
            if client.client_ipv4 and not client.client_ipv6:
                config += 'AllowedIPs = ' + client.client_ipv4 + '\n'
            if client.client_ipv6 and not client.client_ipv4:
                config += 'AllowedIPs = ' + client.client_ipv6 + '\n'
            config += '\n'
        return Response(config, mimetype='text')

