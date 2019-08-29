from flask import Flask
from marshmallow import Schema, fields, pre_load, validate, validates_schema, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from wgpt import app, db

ma = Marshmallow()



class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_description = db.Column(db.String(512))
    client_ipv4 = db.Column(db.String(18))
    client_ipv6 = db.Column(db.String(40))
    client_pubkey = db.Column(db.String(64))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    servers = db.relationship("Server", backref="client")

    def __init__(self, client_ipv4, client_ipv6, client_pubkey, server_id, cluster_id, client_description):
        self.client_ipv4 = client_ipv4
        self.client_ipv6 = client_ipv6
        self.client_pubkey = client_pubkey
        self.server_id = server_id
        self.cluster_id = cluster_id
        self.client_description = client_description

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_description = db.Column(db.String(512))
    server_token = db.Column(db.String(64))
    server_country = db.Column(db.String(256))
    server_city = db.Column(db.String(256))
    server_pubkey = db.Column(db.String(64))
    server_privkey = db.Column(db.String(64))
    server_ip = db.Column(db.String(64))
    server_port = db.Column(db.Integer)
    server_networkv4 = db.Column(db.String(24))
    server_networkv6 = db.Column(db.String(40))
    server_dns = db.Column(db.String(18))
    server_postup = db.Column(db.String(512))
    server_postdown = db.Column(db.String(512))
    server_persistentkeepalive = db.Column(db.Integer)
    server_ssh_key = db.Column(db.String(512))
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    clients = db.relationship("Client", cascade="save-update, merge, delete")

    def __init__(self, server_ip, server_pubkey, server_privkey, server_port, server_networkv4, server_networkv6, server_dns, cluster_id, server_description, server_city, server_country, server_postup, server_postdown, server_token, server_persistentkeepalive, server_ssh_key):
        self.server_description = server_description
        self.server_token = server_token
        self.server_country = server_country
        self.server_city = server_city
        self.server_pubkey = server_pubkey
        self.server_privkey = server_privkey
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_networkv4 = server_networkv4
        self.server_networkv6 = server_networkv6
        self.server_dns = server_dns
        self.server_postup = server_postup
        self.server_postdown = server_postdown
        self.cluster_id = cluster_id
        self.server_persistentkeepalive = server_persistentkeepalive
        self.server_ssh_key = server_ssh_key

class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cluster_description = db.Column(db.String(512))
    cluster_networkv4 = db.Column(db.String(24))
    cluster_networkv6 = db.Column(db.String(40))
    cluster_postup = db.Column(db.String(512))
    cluster_postdown = db.Column(db.String(512))
    cluster_dns = db.Column(db.String(18))
    cluster_privkey = db.Column(db.String(64))
    cluster_pubkey = db.Column(db.String(64))
    cluster_port = db.Column(db.Integer)
    cluster_persistentkeepalive = db.Column(db.Integer)
    clients = db.relationship("Client", cascade="save-update, merge, delete")
    servers = db.relationship("Server", cascade="save-update, merge, delete")

    def __init__(self, cluster_description, cluster_networkv4, cluster_networkv6, cluster_postup, cluster_postdown, cluster_dns, cluster_privkey, cluster_pubkey, cluster_port, cluster_persistentkeepalive):
        self.cluster_description = cluster_description
        self.cluster_networkv4= cluster_networkv4
        self.cluster_networkv6 = cluster_networkv6
        self.cluster_postup = cluster_postup
        self.cluster_postdown = cluster_postdown
        self.cluster_dns = cluster_dns
        self.cluster_privkey = cluster_privkey
        self.cluster_pubkey = cluster_pubkey
        self.cluster_port = cluster_port
        self.cluster_persistentkeepalive = cluster_persistentkeepalive


class ConfigOptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssh_privkey = db.Column(db.String(4096))
    ssh_pubkey = db.Column(db.String(4096))

    def __init__(self, ssh_privkey, ssh_pubkey):
        self.ssh_privkey = ssh_privkey
        self.ssh_pubkey = ssh_pubkey


class ClientSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    client_description = fields.String()
    client_ipv4 = fields.String()
    client_ipv6 = fields.String()
    client_pubkey = fields.String()
    server_id = fields.Integer()
    cluster_id = fields.Integer() 

class ServerSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    cluster_id = fields.Integer(allow_none=True)
    server_description = fields.String(allow_none=True)
    server_token = fields.String(allow_none=False)
    server_pubkey = fields.String(allow_none=True)
    server_privkey = fields.String(allow_none=True)
    server_ip = fields.String()
    server_port = fields.Integer(allow_none=True)
    server_networkv4 = fields.String(allow_none=True)
    server_networkv6 = fields.String(allow_none=True)
    server_dns = fields.String(allow_none=True)
    server_country = fields.String(allow_none=True)
    server_city = fields.String(allow_none=True)
    server_postup = fields.String(allow_none=True)
    server_postdown = fields.String(allow_none=True)
    server_persistentkeepalive = fields.Integer(allow_none=True)
    server_ssh_key = fields.String(allow_none=True)

    @validates_schema
    def validate_ips(self, data, **kwargs):
        if data['server_networkv4'] is None and data['server_networkv6'] is None:
            raise ValidationError('server_networkv4 and server_networkv6 cannot both be empty')

class ClusterServerSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    cluster_id = fields.Integer()
    server_description = fields.String(allow_none=True)
    server_ip = fields.String()
    server_country = fields.String(allow_none=True)
    server_city = fields.String(allow_none=True)

class ClusterSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    cluster_description = fields.String()
    cluster_pubkey = fields.String(allow_none=True)
    cluster_privkey = fields.String(allow_none=True)
    cluster_networkv4 = fields.String(allow_none=True)
    cluster_networkv6 = fields.String(allow_none=True)
    cluster_postup = fields.String(allow_none=True)
    cluster_postdown = fields.String(allow_none=True)
    cluster_dns = fields.String(allow_none=True)
    cluster_persistentkeepalive = fields.Integer(allow_none=True)
    cluster_port = fields.Integer(allow_none=True)

