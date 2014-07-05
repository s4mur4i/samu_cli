import requests
from base import BaseCommand


class Admin(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(args, kwargs)
        self.admin_url = self.app_base_url + '/admin'
        self.endpoint = None
        self.user_id = None
        self.role = None
        self.name = None
        self.value = None
        self.email = None


    def add_arguments(self):
        self.parser.add_argument('--email', default=None, help="Email of admin")
        self.parser.add_argument('--endpoint', default=None, help="REST endpoint to call")
        self.parser.add_argument('--user_id', default=None, help='Used in assigning roles')
        self.parser.add_argument('--role', default=None, help='Used in REST calls involving roles')
        self.parser.add_argument('--name', default=None, help='Used for config endpoint')
        self.parser.add_argument('--value', default=None, help='Used for config endpoint')
        print("Finished adding arguments!")

    def execute(self):
        super(Admin, self).create_parser()
        if not self.endpoint:
            raise Exception("An endpoint must be defined")
        try:
            method = getattr(self, self.endpoint)
            method() #call the method specified in self.endpoint
        except AttributeError as e:
            print(dir(e))
            print(e.msg)
            print("Please enter a correct REST endpoint")

    def register(self):
        payload = {'username': self.username, 'email': self.email,
                'password': self.password}
        resp = requests.post(self.admin_url, data=payload)
        json = resp.json()
        assert json['result'] == 'success'
        return json

    def login(self):
        print("Username " + self.username)
        payload = {'username': self.username, 'password': self.password}
        resp = requests.post(self.admin_url + '/login', data=payload)
        json = resp.json()
        print(json)
        if json:
            #verify that it's a succesful login
            assert json['result'] == 'success'
            if 'sessionid' in json.keys():
                self.session_id = json['sessionid']
                print("Going to write sessionid in file")
                session_file = open(self.session_file_path, mode='w', encoding='utf-8')
                session_file.write(self.session_id)
                session_file.close()
            else:
                raise Exception("Didn't receive session-id after login")
        return json

    def logout(self):
        resp = requests.get(self.admin_url + '/logoff')
        self.session_id = None
        return resp.json()
    def get_user_info(self):
        assert self.session_id is not None
        resp = requests.get(self.admin_url + '/profile/-/' + self.session_id)
        print(resp.json())
        return resp.json()
    
    def update_user_info(self):
        assert self.session_id is not None
        payload = {'username': self.username, 'email': self.email,'password': self.password}
        resp = requests.post(self.admin_url + '/profile/2/-/' + self.session_id, data=payload)
        print(resp.json())
        return resp.json()

    def get_profile(self):
        assert self.session_id is not None
        resp = requests.get(self.admin_url + '/profile/2/-/' + self.session_id)
        print(resp.json())
        return resp.json()
    def delete_profile(self):
        assert self.session_id is not None
        resp = requests.delete(self.admin_url + '/profile/2/-/' + self.session_id)
        print(resp.json())
        return resp.json()
    def list_users(self):
        resp = requests.get(self.admin_url + " /list")
        print(resp.json())
        return resp.json()

    def get_one_user(self):
        resp = requests.get(self.admin_url + "/list/" + self.username)
        print(resp.json())
        return resp.json()
    def get_all_roles(self):
        resp = requests.get(self.admin_url + '/roles')
        print(resp.json())
        return resp.json()
    def assign_userid_to_role(self):
        payload = {'user_id': self.user_id, 'role': self.role}
        resp = requests.post(self.admin_url + '/roles', data=payload)
        return resp.json()
    def delete_role(self):
        payload = {'user_id': self.user_id, 'role': self.role}
        resp = requests.delete(self.admin_url + '/roles')
        return resp.json()
    def get_users_for_role(self):
        resp = requests.get(self.admin_url + '/roles/' + self.role)
        print(resp.json())
        return resp.json() 
    def get_user_configs(self):
        resp = requests.get(self.admin_url + '/profile/ ' + self.user_id + '/configs/-/' + self.session_id)
        print(resp.json())
        return resp.json()
    def set_user_config(self):
        payload = {'name': self.name, 'value': self.value}
        resp = requests.post(self.admin_url + '/profile/ ' + self.user_id + \
                '/configs/-/' + self.session_id, data=payload)
        print(resp.json())
        return resp.json()

    def delete_user_config(self):
        payload = {'name': self.name}
        resp = requests.delete(self.admin_url + '/profile/ ' + self.user_id + 
                '/configs/-/' + self.session_id, data=payload)
        return resp.json()





        
        
        

if __name__ == "__main__":
    a = Admin()
    a.execute()
