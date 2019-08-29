
/* Create a string for combined display of ip addresses */
function createIpString(ipv4, ipv6) {
     if (ipv4 && ipv6) {
        ips = ipv4 + ', ' + ipv6
    }
    if (ipv4 && !ipv6) { 
        ips = ipv4 
    }
    if (!ipv4 && ipv6) { 
        ips = ipv6
    }
    return ips
}


/ * Takes JSON data and transforms it into Wireguard config file for display on page */
function createClientConfigFromJson(target, data){ 
    configFile = '[Interface]\n'
    configFile += 'PrivateKey = ' + data.data.client_privkey + '\n'
    configFile += 'Address = ' + createIpString(data.data.client_ipv4, data.data.client_ipv6) + '\n'
    switch (target) {
        case 'server':
            configFile = '[Interface]\n'
            configFile += 'PrivateKey = ' + data.data.client_privkey + '\n'
            configFile += 'Address = ' + createIpString(data.data.client_ipv4, data.data.client_ipv6) + '\n'
            if (data.data.server_dns) {
                configFile += 'DNS = ' + data.data.server_dns + '\n'
            }
            configFile += '\n'
            configFile += '[Peer]\n'
            configFile += 'PublicKey = ' + data.data.server_pubkey + '\n'
            configFile += 'AllowedIps = 0.0.0.0/0' + '\n'
            configFile += 'Endpoint = ' + data.data.server_ip + ':' + data.data.server_port + '\n'
            configFile += '\n'
            return configFile;
            break;
        case 'cluster':
            configFile = 'Client private key: ' + data.data.client_privkey + '\n'
            configFile += 'Client public key: ' + data.data.client_pubkey + '\n'
            configFile += '\n'
            return configFile
            break;
    }
 
}


/* Populates wg-display-modal with data from json request */
function populateWgDisplayModal(client_id) {
    $.get("/api/clients/get/" + client_id, function(data) {
        $("#wg-display-table").empty();
        if (data.data.client_ipv4) {
            $("#wg-display-table").append('<tr><td>Client IPv4:</td><td>' + data.data.client_ipv4 + '</td></tr>')
        }
        if (data.data.client_ipv6) {
            $("#wg-display-table").append('<tr><td>Client IPv6:</td><td>' + data.data.client_ipv6 + '</td></tr>')
        }
        $("#wg-display-table").append('<tr><td>Public key:</td><td>' + data.data.client_pubkey + '</td></tr>')
    })
    getClientConfig(client_id);
    $("#wg-display-modal").modal('toggle');
}


/* Populates clients table based on server id */
function populateClientsFromServer(server_id){
    $.get("/api/clients/get/by_server_id/" + server_id, function(data) {
        $("#client_table").empty();
        $("#client_table").append('<thead><tr><th>ID</th><th>IP</th><th>Description</th><th>Delete</th></tr></thead>');
        clients = data.data;
        $.each(clients, function(i, item) {
            $('<tr>').html('<td>' + clients[i].id + '</td><td><a href="#" onclick="populateWgDisplayModal(' + clients[i].id + ');return false;">' + createIpString(clients[i].client_ipv4, clients[i].client_ipv6) + '</a></td><td>' + clients[i].client_description + '</td><td><a href="" data-toggle="modal" data-type="client" data-ip="' + clients[i].client_ip + '" data-id="' + clients[i].id + '" data-target="#delete-modal">X</a></td>').appendTo('#client_table');
        })      
    });
}


/* Populates the cluster table based on cluster id */
function populateClientsFromCluster(cluster_id){
    $.get("/api/clients/get/by_cluster_id/" + cluster_id, function(data) {
        $("#client_table").empty();
        $("#client_table").append('<thead><tr><th>ID</th><th>IP</th><th>Description</th><th>Delete</th></tr></thead>');
        clients = data.data;
        $.each(clients, function(i, item) {
            $('<tr>').html('<td>' + clients[i].id + '</td><td><a href="#" onclick="populateWgDisplayModal(' + clients[i].id + ');return false;">' + createIpString(clients[i].client_ipv4, clients[i].client_ipv6) + '</a></td><td>' + clients[i].client_description + '</td><td><a href="" data-toggle="modal" data-type="client" data-ip="' + clients[i].client_ip + '" data-id="' + clients[i].id + '" data-target="#delete-modal">X</a></td>').appendTo('#client_table');
        })      
    });
}


/* Populate server table */
function populateServers(){
    $.get("/api/servers/get/all", function(server_data) {
        $("#server_table").empty();
        $("#server_table").append('<thead><tr><th>ID</th><th>Host</th><th>Delete</th></tr></thead>');
        servers = server_data.data;
        $.each(servers, function(i, item) {
            $('<tr>').html('<td><a href="#" onclick="populateClientsFromServer(' + servers[i].id + ');return false;">' + servers[i].id + '</a></td><td><a href="#" onclick="getServerConfig(' + servers[i].id + ');return false;">' + servers[i].server_ip + '</a></td><td><a href="" data-toggle="modal" data-type="server" data-ip="' + servers[i].server_ip + '" data-id="' + servers[i].id + '" data-target="#delete-modal">X</a></td>').appendTo('#server_table');
        })          
    });
}


/* Populate cluster table */ 
function populateClusters(){
    $.get("/api/clusters/get/all", function(data) {
        $("#cluster_table").empty();
        $("#cluster_table").append('<thead><tr><th>ID</th><th>Description</th><th>Delete</th></tr></thead>');
        clusters = data.data;
        $.each(clusters, function(i, item) {
            $('<tr>').html('<td><a href="#" onclick="populateServers(' + clusters[i].id + ');return false;">' + clusters[i].id + '</a></td><td><a href="#" onclick="getClusterConfig(' + clusters[i].id + ');return false;">' + clusters[i].cluster_description + '</a></td><td><a href="" data-toggle="modal" data-type="cluster" data-ip="' + clusters[i].cluster_network + '" data-cluster="' + clusters[i].cluster_id + '" data-id="' + clusters[i].id + '" data-target="#delete-modal">X</a></td>').appendTo('#cluster_table');
        })          
    });
}


/* Populate servers for clusters table */ 
function populateServersForCluster(cluster_id){
    $.get("/api/servers/get/by_cluster_id/" + cluster_id, function(data) {
        $("#server_table").empty();
        $("#server_table").append('<thead><tr><th>ID</th><th>Network</th><th>Delete</th></tr></thead>');
        servers = data.data;
        $.each(servers, function(i, item) {
            $('<tr>').html('<td>' + servers[i].id + '</td><td><a href="#" onclick="updateClusterServer(' + servers[i].id + ');return false;">' + servers[i].server_ip + '</a></td><td><a href="" data-toggle="modal" data-type="server" data-ip="' + servers[i].server_ip + '" data-id="' + servers[i].id + '" data-cluster="' + servers[i].cluster_id + '" data-target="#delete-modal">X</a></td>').appendTo('#server_table');
        })          
    });
}


/* Populates dropdown select with servers and cluster info used on AddClient modals */ 
function populateInstanceSelect(data){
    if (typeof data.data[0] !== 'undefined') {
        if (data.data[0].hasOwnProperty('cluster_description')) {
            clusters = data.data;
            $("#instance-list").append('<option>Clusters:</option>');
            $.each(clusters, function(i, item) {
                $("#instance-list").append('<option value="cluster_' + clusters[i].id + '">' + clusters[i].id + ' - ' + clusters[i].cluster_description + '</option>');
            })    
        } else {
            servers = data.data;
            $("#instance-list").append('<option>Servers:</option>');
            $.each(servers, function(i, item) {
                $("#instance-list").append('<option value="server_' + servers[i].id + '">' + servers[i].id + ' - ' + servers[i].server_ip + '</option>');
            })
        }
    }
}


/* Generic function for delete of clients, clusters and servers */ 
function deleteThings(delete_type, id){ 

    switch (delete_type) {
        case 'client':
            url = '/api/clients/delete/' + id
            break;
        case 'server':
            url = '/api/servers/delete/' + id
            break;
        case 'cluster':
            url = '/api/clusters/delete/' + id
            break;
    }

    $.ajax(url, {
        type: 'DELETE',
        success: function (data) {

            switch (delete_type) {
                case 'client':
                    fetchClients($('#instance-list').val())
                    break;
                case 'server':
                    populateServers()
                    break;
                case 'cluster':
                    populateClusters();
                    break;
            }
            $('#config-file').empty();
            $('#qrcode').empty();
            if($('#cluster_id').val()) {
                populateServersForCluster($('#cluster_id').val());
            } 
        }
    });
    $('#delete-modal').modal('toggle');
}


/* Generic function to fetch clients, redirects to specific functions */
function fetchClients(id){
    if (id.split('_')[0] == 'server') {
        populateClientsFromServer(id.split('_')[1]);
    } else if (id.split('_')[0] == 'cluster') {
        populateClientsFromCluster(id.split('_')[1]);
    }
}


/* Turn certain values read only when editting a server/cluster */
function flipReadOnly(flip, what){
    $( '#' + what + '_ip' ).prop( "disabled", flip );
    $( '#' + what + '_networkv4' ).prop( "disabled", flip );
    $( '#' + what + '_networkv6' ).prop( "disabled", flip );
    $( '#' + what + '_port').prop( "disabled", flip );
    $( '#' + what + '_pubkey').prop( "disabled", flip );
    $( '#' + what + '_privkey').prop( "disabled", flip );
    $( '#' + what + '_persistentkeepalive').prop( "disabled", flip );
    $( '#' + what + '_dns').prop( "disabled", flip );

    if(flip) {
        $('#add-server-form-btn').hide();
        $('#server_token_div').show();
    } else {
        $('#add-server-form-btn').show();
        $('#server_token_div').hide();
    }

}


/* Fill the form data with json values */
function fillForm(data, what) {
    $.each(data.data, function(name, val){
        var $el = $('[id="'+name+'"]'),
            type = $el.attr('type');
    
        switch(type){
            case 'checkbox':
                $el.attr('checked', 'checked');
                break;
            case 'radio':
                $el.filter('[value="'+val+'"]').attr('checked', 'checked');
                break;
            default:
                $el.val(val);
        }
    });
    
    if (what=='server') {
        flipReadOnly(true, 'server');
        $.get('/api/servers/get/config/' + data.data['id'], function(config) {
            $('#wireguard-config').val(config);
        })
    } else {
        populateServersForCluster(data.data['id']);
        $('#cluster-servers').show();
        $('#add-cluster-form-btn').hide();
        $('#cluster_id').val(data.data['id']);
        flipReadOnly(true, 'cluster');
        $.get('/api/clusters/get/config/' + data.data['id'], function(config) {
            $('#wireguard-config').val(config);
        })
        
    }
    $('#update-server-form-btn').show();
    $('#update-cluster-form-btn').show();
    $('#wireguard-modal-btn').show();
}


/* Clear the form */
function clearForm(what){
    $('#server_form').trigger("reset");
    $('#wireguard-modal-btn').hide();
    $('#cluster-servers').hide();
    $('#update-cluster-form-btn').hide();
    $('#update-server-form-btn').hide();
    $('#add-cluster-form-btn').show();
    flipReadOnly(false, what);
}


/* Get server config and display */
function getServerConfig(server_id) {
    $.get("/api/servers/get/" + server_id, function(data){
        fillForm(data, 'server');        
    })
}


/* Get server config and display */
function getClusterConfig(cluster_id) {
    $.get("/api/clusters/get/" + cluster_id, function(data){
        fillForm(data, 'cluster');
    })
}


/* Get client config and display */
function getClientConfig(client_id) {
    $.get("/api/clients/get/" + client_id, function(data){
        $('#config-file').empty();
        client_config = '[Peer]\nPublicKey = ' + data.data.client_pubkey  + '\n'
        client_config += 'AllowedIPs = ' + createIpString(data.data.client_ipv4, data.data.client_ipv6);
        $('#server-config-file').html('<pre>' + client_config + '</pre>')

    })
}


/* Function to update cluster server information */
function updateClusterServer(server_id) { 
    getServerConfig(server_id);
    $('#add-server-to-cluster-modal').modal('toggle');
    $('#add-server-to-cluster-modal-btn').hide();
    $('#update-server-to-cluster-modal-btn').show();
}


/* Function to display return messages as modal in page (not fully implemented) */
function displayMessage(message) {
    $('#message-modal-body').empty();
    $('#message-modal-body').html(message);
    $('#message-modal').modal('toggle');
}


/* Set empty form values to null */ 
function nullIfEmpty(key, value) {
    if (value == '') {
        return null;
    } else {
        return value;
    }
}