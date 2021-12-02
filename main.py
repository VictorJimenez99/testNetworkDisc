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
                return value
        except NetmikoAuthenticationException:
            print("auth_error")
        except NetmikoTimeoutException:
            print("Timeout Error")
        except Exception as e:
            print(f"Some other error: {e}")

    def add_connection(self, router):
        self.connected_to.append(router)

    def __eq__(self, other):
        return self.destination_host == other.destination_host


def discover_topology(gateway_router: RouterDiscovery):
    user_name_unique = gateway_router.username
    password_unique = gateway_router.password
    discovered_routers: [] = [gateway_router]
    index = 0
    finished: bool = False

    while not finished:
        try: single_router = discovered_routers[index]
        except IndexError:
            print("finished")
            finished = True
            continue

        neighbors_data = single_router.show_neighbors()
        for unique_data in neighbors_data:
            single_router = RouterDiscovery(unique_data.ip,
                                            user_name_unique,
                                            password_unique,
                                            unique_data.destination_host)
            single_router.add_connection(single_router)
            if single_router not in discovered_routers:
                discovered_routers.append(single_router)
        index += 1

    return discovered_routers


if __name__ == "__main__":
    print("hola")
    router = RouterDiscovery(ip="10.1.0.254", username="admin", password="admin", destination_host="R1.Red1.com")
    print(router.show_neighbors())
    print(discover_topology(router))
