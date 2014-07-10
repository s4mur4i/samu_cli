import os
from configparser import SafeConfigParser
import argparse


CURRENT_DIR = os.path.dirname(__file__)
class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.cfg_parser = SafeConfigParser()
        self.cfg_parser.read("../app_config.cfg")
        self.username = self.cfg_parser.get('app_level', 'username')
        self.password = self.cfg_parser.get('app_level', 'password') 
        self.app_base_url = self.cfg_parser.get('app_level', 'app_base_url')
        self.args = None
        self.session_id = None
        self.session_file_path = os.path.join(CURRENT_DIR, 'session_info.txt')
        self.get_sessionid()
    def create_parser(self):
        
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--username', help="Username used to login", \
                default=self.username)
        self.parser.add_argument('--password', help='Password used to login',\
                default=self.password)
        self.parser.add_argument('--app_base_url', help="Application's base URL", \
                default=self.app_base_url)
        self.parser.add_argument('--endpoint', default=None, help="REST endpoint to call")
        self.parser.add_argument('--session_id')
        self.add_arguments()
        self.args = self.parser.parse_args(namespace=self)

    def login(self):
        print("Username " + self.username)
        payload = {'username': self.username, 'password': self.password}
        url = self.app_base_url +"/admin"
        resp = requests.post(url, data=payload)
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


    def add_arguments(self):
        """
        Entrypoint for subclasses to add arguments
        """
        pass
    def test(self):
        print('test called')
    def execute(self):
        self.create_parser()
        if not self.endpoint:
            raise Exception("An endpoint must be defined")
        try:
            method = getattr(self, self.endpoint)
            method() #call the method specified in self.endpoint
        except AttributeError as e:
            print("Please enter a correct REST endpoint")

    def get_sessionid(self):
        session_file = None 
        try:
            session_file = open(self.session_file_path, encoding='utf-8')
        except IOError:
            self.session_id = None
        else:
            self.session_id = session_file.read() or None
            session_file.close()


# = BaseCommand()
#.create_parser()
#rint b.session_id
#rint type(b.args)
#rint b.execute()
