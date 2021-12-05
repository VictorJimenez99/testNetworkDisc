from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException


class RouterDiscovery:
    def __init__(self, ip: str, username: str, password: str, destination_host: str):
        self.destination_host = destination_host
        self.ip: str = ip
        self.username = username
        self.device_type: str = "cisco_ios_telnet"
        self.connected_to: [] = []
        self.password: str = password

    def show_neighbors(self):
        device = {
            'device_type': self.device_type,
            'ip': self.ip,
            'username': self.username,
            'password': self.password
        }
        try:
            with ConnectHandler(**device) as connector:
                value = connector.send_command('show cdp neighbors detail', use_textfsm=True)
                for rout in value:
                    self.add_connection(rout.get("destination_host"))
                return value
        except NetmikoAuthenticationException:
            print("auth_error")
        except NetmikoTimeoutException:
            print("Timeout Error")
        except Exception as e:
            print(f"Some other error: {e}")

    def add_connection(self, router_name):
        self.connected_to.append(router_name)

    def __eq__(self, other):
        return self.destination_host == other.destination_host

    def __repr__(self):
        return f"RD: {self.destination_host}"


def discover_topology(gateway_router: RouterDiscovery):
    user_name_unique = gateway_router.username
    password_unique = gateway_router.password
    discovered_routers: [] = [gateway_router]
    index = 0
    finished: bool = False

    while not finished:
        try:
            single_router = discovered_routers[index]
        except IndexError:
            print("finished")
            finished = True
            continue

        neighbors_data = single_router.show_neighbors()

        for unique_data in neighbors_data:
            unique_data_dest_host = unique_data.get("destination_host")
            single_router = RouterDiscovery(unique_data.get("management_ip"),
                                            user_name_unique,
                                            password_unique,
                                            unique_data_dest_host)
            # single_router.add_connection(unique_data_dest_host)
            if single_router not in discovered_routers:
                discovered_routers.append(single_router)
        index += 1

    # print(discovered_routers)
    return discovered_routers


if __name__ == "__main__":
    print("hola")
    router_test = RouterDiscovery(
        ip="10.1.0.254", username="admin",
        password="admin", destination_host="R1.red1.com")
    discovered_topology = discover_topology(router_test)
    for r in discovered_topology:
        print(f"{r.destination_host} is connected to: {r.connected_to}")
