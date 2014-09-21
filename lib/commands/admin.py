import requests
from base import BaseCommand


class Admin(BaseCommand):
    """
    Admin class provides interactions with http://url.com/admin. As for
    the login, it takes 'username' and 'password' from the config file.
    Once a user is logged in it writes the session in a file named 
    session_info.txt (which is in the same directory where base.py is
    placed). We save session-id in the session_info so user doesn't have
    to type session-id for all subsequent calls.

    Usage: 
    It takes username, password from the config file but they can
    also be supplied from the command line so for example one can 
    register by issugin the following command
    >>python admin.py --endpoint register --username user --email someemail --password
    
    and if all goes well user will be registered. Notice the '--endpoint' 
    argument. This argument maps to class methods which in turn maps to actual
    URI endpoints. So for example, if you want to logout you do
    >> python admin.py --endpoint logout.

    If you wantt to get info of the user you do
    >> python admin.py --endpoint get_user_info

    All other examples are given in comments below.
    """
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
        self.parser.add_argument('--user_id', default=None, help='Used in assigning roles')
        self.parser.add_argument('--role', default=None, help='Used in REST calls involving roles')
        self.parser.add_argument('--name', default=None, help='Used for config endpoint')
        self.parser.add_argument('--value', default=None, help='Used for config endpoint')
        print("Finished adding arguments!")

    def register(self):
        """
        Usage:
        >> python admin.py --username user --email email --password pwd --endpoint register
        """
        payload = {'username': self.username, 'email': self.email,
                'password': self.password}
        resp = requests.post(self.admin_url, data=payload).json()
        print(resp)
        return resp['result']

    def execute(self):
        self.create_parser()
        if not self.endpoint:
            raise Exception("An endpoint must be defined")
        try:
            method = getattr(self, self.endpoint)
            data = method() #call the method specified in self.endpoint
            self.output(data, self.to_csv, self.to_table)
        except AttributeError as e:
            print(e)
            print("Please enter a correct REST endpoint")
            print(self.parser.print_help())
    
    def show_all(self):
        print("""
            1- register 
            2- verify_login
            3- logout
            4- get_user_info
            5- update_user_info
            6- get_profile
            7- delete_profile
            8- list_users
            9- get_one_user
            10- assign_userid_to_role
            11- delete_role
            12- get_users_for_role
            13- get_user_configs
            14- set_user_config
            15- delete_user_config
            16- list_roles
            """)
    
    def verify_login(self):
        if not self.session_id:
            print("Wait, trying to login first...")
            self.login()
     
    def logout(self):
        """
        Usage:
        >> python admin.py --endpoint logout
        TODO: Remove sesion from session_info.txt on logout.
        """
        resp = requests.get(self.admin_url + '/logoff').json()
        self.session_id = None
        print(resp)
        return resp['result']
    def get_user_info(self):
        """
        Usage: 
        User needs to be logged in. Call to /admin/profile/-/session-id is sent
        >> python admin.py --endpoint get_user_info
        """
        self.verify_login()
        assert self.session_id is not None
        resp = requests.get(self.admin_url + '/profile/-/' + self.session_id).json()
        print(resp)
        return resp['result']
    
    def update_user_info(self):
        """
        Usage: 
        Updates a user and call to /admin/profile/user-id/-/session-id is sent
        >> python admin.py --endpoint update_user_info --username user --email email --password pwd --user_id 5
        """

        self.verify_login()
        assert self.session_id is not None
        payload = {'username': self.username, 'email': self.email,'password': self.password}
        print(payload)
        resp = requests.post(self.admin_url + '/profile/' + self.user_id + '/-/' + self.session_id, data=payload).json()
        print(resp)
        return resp['result']

    def get_profile(self):
        """
        Usage:
        Gets profile and call to /admin/profile/user-id/-/session-id is sent. User
        needs to be logged in.
        >> python admin.py --endpoint get_profile --user_id 5
        """

        self.verify_login()
        assert self.session_id is not None
        assert self.user_id is not None
        resp = requests.get(self.admin_url + '/profile/' + self.user_id + '/-/' + self.session_id).json()
        print(resp)
        return resp['result']

    def delete_profile(self):
        """
        Usage:
        Deletes a profile and call to /admin/profile/user-id/session-id is sent
        >> python admin.py --endpoint delete_profile --user_id 5
        """

        self.verify_login()
        assert self.session_id is not None
        assert self.user_id is not None
        resp = requests.delete(self.admin_url + '/profile/' + self.user_id + '/-/' + self.session_id).json()
        print(resp)
        return resp['result']

    def list_users(self):
        """
        Usage:
        Lists users and a call to /admin/list is sent
        >> pyhton admin.py --endpoint list_users
        """
        url = self.admin_url + "/list"
        print("Request URL: " + url)
        resp = requests.get(url).json()
        print(resp)
        return resp['result']

    def get_one_user(self):
        """
        Usage:
        Gets list of one user and call to /admin/list/username is sent 
        >> python admin.py --endpoint get_one_user --username someuser
        """
        resp = requests.get(self.admin_url + "/list/" + self.username).json()
        print(resp)
        return resp['result']

    def assign_userid_to_role(self):
        """
        Usage:
        Assigns a role to user-id
        >> python admin.py --endpoint assign_userid_to_role --user_id 4 --role somerole
        >>To add a user to a role:

        s4mur4i@hanoi:~/workspace/samu/lib/SamuRest/Controller$ curl -X POST -d 'user_id=3&role=privilege' 
        http://localhost:3000/admin/roles/privilege/-/7...
        {"status":"success","result":[{"id":3}]}
        """
        payload = {'user_id': self.user_id, 'role': self.role}
        url = self.admin_url + '/roles/' + self.role + "/-/" + self.session_id
        print("Requesting: " + url)
        resp = requests.post(url, data=payload).json()
        print(resp)
        return resp['result']
    def delete_role(self):
        """
        Usage:
        Deletes a role and used as below.
        >> python admin.py --endpoint delete_role --user_id 3 --role somerole
        >>curl -X DELETE -d 'user_id=3&role=privilege' http://localhost:3000/admin/roles/privilege/-/7...

        """
        payload = {'user_id': self.user_id, 'role': self.role}
        url = self.admin_url + '/roles/' + self.role + "/-/" + self.session_id
        print("Requesting: " + url)
        resp = requests.delete(url).json()
        print(resp)
        return resp['result']
    def get_users_for_role(self):
        """
        Usage:
        Get users for a given role and call is sent to 
        /admin/roles/somerole
        Usage:
        >> python admin.py --endpoint get_users_for_role --role somerole
        """
        url = self.admin_url + '/roles/' + self.role
        print("Requesting: " + url)
        resp = requests.get(url).json()
        print(resp)
        return resp['result']
    
    def list_roles(self):
        """
        s4mur4i@hanoi:~/workspace/samu/lib/SamuRest/Controller$ curl -X GET 
        http://localhost:3000/admin/roles/-/771ef51492d...
        {"status":"success","result":[{"1":"admin"},{"2":"guest"},{"3":"registered"},{"4":"privilege"}]}
        """
        url = self.admin_url + '/roles/-/' + self.session_id
        print("Requesting: " + url)
        resp = requests.get(url).json()
        print(resp)
        return resp['result']

    def get_user_configs(self):
        """
        Usage:
        Get user configs and call to 
        /admin/profile/user-id/configs/-/session-id is sent
        >> python admin.py --endpoint get_user_configs --user_id 3
        """

        self.verify_login()
        url = self.admin_url + '/profile/' + self.user_id + '/configs/-/' + self.session_id 
        print(url)
        resp = requests.get(url).json()
        print(resp)
        return resp['result']

    def set_user_config(self):
        """
        Usage:
        Sets user configs and call to 
        /admin/profile/user-id/configs/-/session-id is sent
        >> python admin.py --endpoint set_user_config --user_id 2 --name name --value value
        >>curl -X POST -d 'name=vcenter_username&value=test2' http://localhost:3000/admin/profile/3/configs/-...
        {"status":"success","result":[{"data":"test2","config_id":2}]}
        """

        self.verify_login()
        assert self.session_id is not None
        assert self.user_id is not None
        payload = {'name': self.name, 'value': self.value}
        url = self.admin_url + '/profile/' + self.user_id + '/configs/-/' + self.session_id
        print("Request URL: " + url)
        resp = requests.post(url, data=payload).json()
        print(resp)
        return resp['result']

    def delete_user_config(self):
        """
        Usage:
        Delete user configs and call to
        /admin/profile/user-id/configs/-/session-id is sent
        >> python admin.py --endpoint delete_user_configs --user_id 4 --name name
        >>curl -X DELETE -d 'name=vcenter_username' http://localhost:3000/admin/profile/3/configs/-...
        {"status":"success","result":[{}]}
        """

        self.verify_login()
        assert self.session_id is not None
        payload = {'name': self.name}
        url = self.admin_url + '/profile/' + self.user_id + '/configs/-/' + self.session_id
        print("Requesting: " + url)
        resp = requests.delete(url, data=payload).json()
        print(resp)
        return resp['result']



if __name__ == "__main__":
    a = Admin()
    a.execute()
