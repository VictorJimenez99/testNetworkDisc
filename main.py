from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from collections import namedtuple




class RouterDiscovery:
    def __init__(self, ip: str,username: str, password: str):
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
        except Exception:
            print("Some other error")



if __name__ == "__main__":
    print("hola")
    router = RouterDiscovery(ip="10.1.0.254", username="admin", password="admin")
    print(router)