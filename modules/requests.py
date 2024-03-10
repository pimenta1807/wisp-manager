import configparser
import requests

config = configparser.ConfigParser()
config.read('config.ini')

status_codes = {
    -1: 'Error',
    0: 'Offline',
    1: 'Online',
    2: 'Starting',
    3: 'Stopping',
    10: 'Migrating',
    20: 'Installing',
    21: 'FailedInstall',
    30: 'Suspended',
    31: 'Updating',
    32: 'Moving',
    40: 'CreatingBackup',
    41: 'DeployingBackup',
}

def prepare_request(api_type):
    """Returns the URL and headers for the request.
    The URL is defined in the config.ini file."""

    # Some functions (rebuild, for example) require the admin api.
    if api_type == "admin":
        url = "https://" + config['Panel']['url'] + "/api/admin/servers/"
    else:
        url = "https://" + config['Panel']['url'] + "/api/client/servers/"

    headers = {
        "Authorization": f"Bearer {config['API']['key']}",
        "Content-Type": "application/json",
        "Accept": "Application/vnd.wisp.v1+json",
    }
    return url, headers

def get_data():
    """Returns a generator of all servers data."""


    base_url, headers = prepare_request("client")
    params = {'include': 'node,egg,allocations'}
    page = 1
    while True:
        params['page'] = page
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            data = response.json()
            if not data['data']:  # If there is no more data, break the loop.
                break
            yield from data['data']  # Yielding the data of all pages.
            page += 1
        except requests.exceptions.RequestException as e:
            print(f'An error occurred: {e}')
            break

def process_data(servers):
        """Process the data of all servers in the list."""


        servers_data = list(get_data())  # Avoids processing all data at once.
        servers = []
        for server_data in servers_data:
            server = server_data['attributes']
            server['allocations'] = [a['attributes'] for a in server['relationships']['allocations']['data']]
            server['node'] = server['relationships']['node']['attributes']
            server['egg'] = server['relationships']['egg']['attributes']
            servers.append(server)
        return servers # Returns a list of dictionaries.

def process_online_servers(servers):
    """Process the status of all servers in the list.
    The status is processed in parallel using ThreadPoolExecutor.
    The status is then added to the server dictionary."""


    from concurrent.futures import ThreadPoolExecutor        
    with ThreadPoolExecutor() as executor: # Creates a thread pool to make requests in parallel.
        statuses = executor.map(get_server_status, servers) # Map the get_server_status function to each server.
    for server, status in zip(servers, statuses): # Iterates through the servers and set their statuses.
        server['status'] = status_codes.get(status, 'Unknown') 


def get_server_status(server):
    """Returns the server status code. If the server is online, the status code is 1. 
    If it's offline, the status code is 0. And so on."""


    url, headers = prepare_request("client")
    # If before the URL was "https://panel.gg/api/client/servers/", now it is "https://panel.gg/api/client/servers/{uuid}/resources/"
    url = url + f"{server['uuid_short']}/resources"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTPError if the status is 4xx, 5xx
        data = response.json()
        if data and 'status' in data:
            return data['status']
        elif 'errors' in data and data['errors'][0]['code'] == 'server.errors.suspended': #idk why it's returning error instead of 30. gonna hack it
            return 30 
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')
        print(f'Response: {response.content}')
        return None