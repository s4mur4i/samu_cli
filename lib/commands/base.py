import pandas
import requests
import os
import sys
import csv
from configparser import SafeConfigParser
import argparse
from prettytable import PrettyTable

CURRENT_DIR = os.path.dirname(__file__)
class BaseCommand(object):

    def __init__(self, *args, **kwargs):
        self.cfg_parser = SafeConfigParser()
        config_path = os.path.normpath(CURRENT_DIR + "/app_config.cfg")
        self.cfg_parser.read(config_path)
        self.username = self.cfg_parser.get('app_level', 'username')
        self.password = self.cfg_parser.get('app_level', 'password') 
        self.app_base_url = self.cfg_parser.get('app_level', 'app_base_url')
        self.args = None
        self.session_id = None
        self.csv = None
        self.session_file_path = os.path.join(CURRENT_DIR, 'session_info.txt')
        self.get_sessionid()
    def to_csv(self, data, rows, values):
        """
        data is usually json object returned, rows is number of rows
        whereas values is usually pertinent json object keys that can
        be used as columns
        """
        row = PrettyTable()
        row.field_names = data.keys()
        row.add_row(data.values())
        print(row.get_string())

        writer = csv.DictWriter(sys.stdout, delimiter=',', fieldnames = values)
        writer.writeheader()
        return writer.writerow(data)
        #pd = pandas.DataFrame(data, index=rows, columns=values)
        #print(pd)
        #return pd.to_csv()

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
        self.parser.add_argument('--csv')
        self.add_arguments()
        self.args = self.parser.parse_args(namespace=self)

    def login(self):
        print("Username " + self.username)
        payload = {'username': self.username, 'password': self.password}
        url = self.app_base_url + "/admin/login"
        resp = requests.post(url, data=payload)
        json = resp.json()
        rows= [0]
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
        return json, rows, json.keys()


    def add_arguments(self):
        """
        Entrypoint for subclasses to add arguments
        """
        pass
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
