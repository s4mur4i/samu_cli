import requests
from base import BaseCommand

class Admin(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(args, kwargs)
        self.admin_url = self.base_url + '/admin'
        self.endpoint = None
    def add_arguments(self):
        self.parser.add_argument('--email', help="Email of admin")
        self.parser.add_argument('--endpoint', help="REST endpoint to \
                call", default=self.endpoint)
        self.parser.add_argument('--user_id', help='Used in assigning roles')
        self.parser.add_argument('--role', help='Used in REST calls involving roles')
        self.parser.add_argument('--name', help='Used for config
        endpoint')
        self.parser.add_argument('--value', help-'Used for config
        endpoint')

    def execute(self):
        try:
            method = getattr(self, self.endpoint)
        except AttributeError, e:
            print "Please enter a correct REST endpoint, cannot find \
            implementation of this endpoint"

    def register(self):
        payload = {'username': self.username, 'email': self.email,
                'password': self.password}
        resp = requests.post(self.admin_url, data=payload)
        return resp.text

    def login(self):
        payload = {'username': self.username, 'password': self.password}
        resp = requests.post(self.admin_url + '/login')
        #TODO: store session id
        return resp.text

    def logout(self):
        resp = requests.get(self.admin_url + '/logoff')
        self.session_id = None
        return resp.text
    def get_user_info(self):
        assert self.session_id is not None
        return requests.get(self.admin_url + '/profile/-/' + self.session_id)
    
    def update_user_info(self):
        assert self.session_id is not None
        data = {'username': self.username, 'email': self.email,'password': self.password}
        resp = requests.post(self.admin_url + '/profile/2/-/' + self.session_id)
        return resp.text

    def get_profile(self):
        assert self.session_id is not None
        return requests.get(self.admin_url + '/profile/2/-/' + self.session_id)

    def delete_profile(self):
        assert self.session_id is not None
        return requests.delete(self.admin_url + '/profile/2/-/' + self.session_id)

    def list_users(self):
        return requests.get(self.admin_url + " /list").text

    def get_one_user(self):
        return requests.get(self.admin_url + "/list/" + self.username).text

    def get_all_roles(self):
        return requests.get(self.admin_url + '/roles').text

    def assign_userid_to_role(self):
        payload = {'user_id': self.user_id, 'role': self.role}
        return requests.post(self.admin_url + '/roles').text

    def delete_role(self):
        payload = {'user_id': self.user_id, 'role': self.role}
        return requests.delete(self.admin_url + '/roles').text

    def get_users_for_role(self):
        return requests.get(self.admin_url + '/roles/' + self.role).text
    
    def get_user_configs(self):
        return requests.get(self.admin_url + '/profile/ ' + self.user_id + '/configs/-/' + self.session_id)

    def set_user_config(self):
        payload = {'name': self.name, 'value': self.value}
        resp = requests.post(self.admin_url + '/profile/ ' + self.user_id + \
                '/configs/-/' + self.session_id, data=payload)

        return resp.text

    def delete_user_config(self):
        payload = {'name': self.name}
        resp = requests.delete(self.admin_url + '/profile/ ' + self.user_id + 
                '/configs/-/' + self.session_id, data=payload)
        return resp.text





        
        
        


a = Admin()
a.create_parser()
print a.args
