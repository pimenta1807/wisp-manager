from modules import requests as lrequests # local requests, to avoid conflicts with the original requests module. i'm not feeling creative :(
import requests

def format_name(name):
    """Format the server name to fit in the terminal."""

    return name[:21] + "..." if len(name) > 24 else name

def select_node(data):
    """Select a node to list the servers."""


    nodes = list(set(server['node']['name'] for server in data))
    node_dict = {i+1: node for i, node in enumerate(nodes)}
    for i, node in node_dict.items():
        print(f"Node {i}: {node}")

    input_node = int(input("Select a node: "))
    selected_node = node_dict.get(input_node)
    if selected_node is None:
        print("Invalid option")
        return
    return selected_node


def list_all(servers):
    """List all servers."""


    for server in servers:
        status = server['status']
        name = format_name(server['name'])
        print(f"Name: {name:<24}, Status: {status:<9}, node: {server['node']['name']}, uuid_short: {server['uuid_short']},")


def list_by_node(servers, node):
    """List servers by node."""

    for server in servers:
        if server['node']['name'] == node:
            name = format_name(server['name'])
            status = server['status']
            print(f"Name: {name:<24}, Status: {status:<9}, uuid_short: {server['uuid_short']},")
        

def shutdown_all(servers):
    """Shutdown all online servers."""

    i, j, k = 0, 0, 0
    url, headers = lrequests.prepare_request("client")
    for server in servers:
        if server['status'] == 'Online':
            url = url + f"{server['uuid_short']}/power"
            data = {
                "signal": "stop"
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 204:
                    print(f'Successfully sent shutdown signal to server "{server["name"]}".')
                else:
                    response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            except requests.exceptions.RequestException as e:
                print(f'An error occurred: {e}')
                print(f'Response: {response.content}')
            i += 1
        elif server['status'] == 'Offline':
            print(f"Server {server['name']} is already offline.")
            j += 1
        else: 
            print(f"Server {server['name']} skipped: {server['status']}.")
            k += 1
    print(f'\n\n{i} servers were successfully shutdown, {j} servers were already offline, {k} servers were ignored (suspended).\n\n')


def shutdown_by_node(servers, node):
    """Shuts down all online servers from a specific node."""
    
    i, j, k = 0, 0, 0
    url, headers = lrequests.prepare_request("client")
    for server in servers:
        if server['node']['name'] == node:
            if server['status'] == 0:
                print(f'Server "{server["name"]}" is already offline.')
                i += 1
            elif server['status'] == 1:
                url = url + f"{server['uuid_short']}/power"
                data = {
                    "signal": "stop"
                }
                try:
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 204:
                        print(f'Successfully sent shutdown signal to server "{server["name"]}".')
                    else:
                        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
                except requests.exceptions.RequestException as e:
                    print(f'An error occurred: {e}')
                    print(f'Response: {response.content}')
                j += 1
            elif server['status'] == 2:
                print(f'Server "{server["name"]}" is suspended.')
                k += 1
    print(f'\n\n{j} servers were successfully shutdown, {i} servers were already offline, {k} servers were ignored (suspended).\n\n')


def rebuild_containers_all_servers(servers):
    """Rebuilds the server container"""


    url, headers = lrequests.prepare_request("admin")

    for server in servers:
        url = url + f"{server['id']}/rebuild"
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            print(f'Successfully sent rebuild signal to server "{server["name"]}".')
        except requests.exceptions.RequestException as e:     
            print(f'An error occurred: {e}')
            print(f'Response: {response.content}')

def rebuild_containers_by_node(servers, node):
    """Rebuilds the server container"""

    url, headers = lrequests.prepare_request("admin")

    for server in servers:
        if server['node']['name'] == node:
            url = url + f"{server['id']}/rebuild"

            try:
                response = requests.post(url, headers=headers)
                response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
                print(f'Successfully sent rebuild signal to server "{server["name"]}".')
            except requests.exceptions.RequestException as e:     
                print(f'An error occurred: {e}')
                print(f'Response: {response.content}')