
from modules import server_management, requests

def main():

    # url and headers are defined in requests.py

    print("Fetching all servers...")
    # A request is made to the API that returns a list of dictionaries of all servers that the api_key has access to.
    servers = list(requests.get_data())
    print(f"Servers found: {len(servers)}")

    # Process the data of all servers in the dictionary list
    servers = requests.process_data(servers)
    print("Servers parsed.\n")

    # Process the status of all servers in the list.
    print("Fetching servers status...")
    requests.process_online_servers(servers) 

    online_servers = len([server for server in servers if server['status'] == 'Online'])
    print(f"Online servers found: {online_servers}\n")

    while True:
        print("""1. List servers by node.
2. Rebuild servers containers by node.
3. Shutdown servers by node. (atm only prints expected output, edit in server_management.py)
4. List all servers.
5. Rebuild all servers containers.
6. Shutdown all servers (atm only prints expected output, edit in server_management.py).
99. Exit""")
        option = input("\nSelect an option: ")

        if option == '1': 
            node = server_management.select_node(servers)
            server_management.list_by_node(servers, node) # List servers by node.
        elif option == '2': 
            node = server_management.select_node(servers)
            server_management.rebuild_containers_by_node(servers, node) # Rebuid os containers dos servidores por nó.
        elif option == '3': 
            node = server_management.select_node(servers)
            server_management.shutdown_by_node(servers, node) # Shutdown servers by node.
        elif option == '4':
            server_management.list_all(servers)  # List all servers.
        elif option == '5': 
            server_management.rebuild_containers_all_servers(servers) # Rebuild all servers containers.
        elif option == '6': 
            server_management.shutdown_all(servers)  # Shutdown all servers.
        elif option == '99':
            break
        else:
            print("Invalid option. Please try again.")

main()