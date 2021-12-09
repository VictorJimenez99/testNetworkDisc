from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException


class RouterDiscovery:
    def __init__(self, ip: str, username: str, password: str, destination_host: str):
        self.destination_host = destination_host
        self.ip: str = ip
        self.username = username
        self.device_type: str = "cisco_ios_telnet"
        self.connected_to: [] = []  # router info dictionary
        self.password: str = password
        self.protocol: str = "unknown"

    def show_neighbors(self):
        ospf_id = "O"
        rip_id = "R"
        eigrp_id = "D"

        device = {
            'device_type': self.device_type,
            'ip': self.ip,
            'username': self.username,
            'password': self.password
        }
        neighbors = []
        try:
            with ConnectHandler(**device) as connector:
                protocol = connector.send_command('show ip route', use_textfsm=True)
                router_protocol = ""
                # Since it is assumed that there will only be one and only one
                # protocol at a given moment one match is more than enough to
                # identify the current config of the router
                for connection in protocol:
                    possible_protocol_id = connection.get("protocol")
                    if possible_protocol_id == ospf_id:
                        router_protocol = "OSPF"
                        break
                    elif possible_protocol_id == rip_id:
                        router_protocol = "RIP"
                        break
                    elif possible_protocol_id == eigrp_id:
                        router_protocol = "EIGRP"
                        break
                    else:
                        router_protocol = "UNKNOWN"

                # print(f"protocol: {router_protocol}")
                self.protocol = router_protocol
                neighbors = connector.send_command('show cdp neighbors detail', use_textfsm=True)
                for rout in neighbors:
                    self.add_connection(rout)
                return neighbors
        except NetmikoAuthenticationException:
            print("auth_error")
        except NetmikoTimeoutException:
            print("Timeout Error")
            return neighbors
        except Exception as e:
            print(f"Some other error for router {self.destination_host}: {e}")

    def add_connection(self, router_info):
        self.connected_to.append(router_info)

    def __eq__(self, other):
        return self.destination_host == other.destination_host

    def __repr__(self):
        data_connection: [] = []
        for dest in self.connected_to:
            data_connection.append(dest.get("destination_host"))
        return f"RD: {self.destination_host}, ip:addr: {self.ip}, " \
               f"protocol: {self.protocol}, connected_to: {data_connection}"


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
        if neighbors_data is None:
            continue

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
    while True:
        router_test = RouterDiscovery(
            ip="10.1.0.254", username="admin",
            password="admin", destination_host="R1.red1.com")
        discovered_topology = discover_topology(router_test)
        routers = []
        connections = []

        for r in discovered_topology:
            routers.append({"name": r.destination_host, "ip_addr": r.ip, "protocol": r.protocol})
            appended = []
            for con in r.connected_to:
                appended.append({"source": r.destination_host, "destination": con.get("destination_host")})
            connections += appended
            payload = {"routers": routers,
                       "connections": connections}

            print(payload)