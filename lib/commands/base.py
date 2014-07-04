from configparser import SafeConfigParser
import argparse

class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.cfg_parser = SafeConfigParser()
        self.cfg_parser.read("../app_config.cfg")
        self.username = self.cfg_parser.get('app_level', 'username')
        self.password = self.cfg_parser.get('app_level', 'password') 
        self.app_base_url = self.cfg_parser.get('app_level', 'app_base_url')
        self.args = None
        self.session_id = None
    def create_parser(self):
        
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--username', help="Username used to login", \
                default=self.username)
        self.parser.add_argument('--password', help='Password used to login',\
                default=self.password)
        self.parser.add_argument('--app_base_url', help="Application's base URL", \
                default=self.app_base_url)
        self.parser.add_argument('--session_id')
        self.add_arguments()
        self.args = self.parser.parse_args(namespace=self)

    def add_arguments(self):
        """
        Entrypoint for subclasses to add arguments
        """
        pass
    def test(self):
        print('test called')
    def execute(self):
        print(getattr(self, 'testsds')())


# = BaseCommand()
#.create_parser()
#rint b.session_id
#rint type(b.args)
#rint b.execute()
