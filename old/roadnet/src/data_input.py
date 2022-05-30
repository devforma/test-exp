import requests

class Data_input:
    def __init__(self, input_path, dp_address, city, longtitude, latitude):
        self.dp_address = dp_address
        self.input_path = input_path
        self.city = city
        self.longtitude = longtitude
        self.latitude = latitude

    def from_odps(self):
        print("Getting data from odps......")
        # http request

        params = {
            "dpAddress": self.dp_address,
            "payload": {
                "body": ""
            }
        }
        r = requests.post("", json=params)
        content = r.json()

        with open(self.input_path + '/node.csv', 'w') as f:
            f.write(content)

        with open(self.input_path + '/edge1.csv', 'w') as f:
            f.write(content)

        with open(self.input_path + '/edge2.csv', 'w') as f:
            f.write(content)