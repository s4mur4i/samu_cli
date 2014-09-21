import pandas
import requests
import os
import sys
import csv
from configparser import SafeConfigParser
from datetime import datetime, timedelta
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
        self.to_csv = None
        self.table = None
        self.session_file_path = os.path.join(CURRENT_DIR, 'session_info.txt')
        self.get_sessionid()
        self.session_timestamp = None

    def output(self, data, to_csv=False, to_table=False):
        try:
            if data and data[0]:
                field_names = list(data[0].keys())
        except:
            raise Exception("Data disctionary not correctly defined")
        if to_table and field_names:
            table = PrettyTable()
            table.field_names = field_names
            table.max_width = 80
            for item in data:
                table.add_row(list(item.values()))
            print(table)
        if to_csv:
            writer = csv.DictWriter(sys.stdout, delimiter=';', fieldnames = field_names)
            writer.writeheader()
            for item in data:
                writer.writerow(item) 
  
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
        self.parser.add_argument('--to_csv')
        self.parser.add_argument('--to_table')
        self.add_arguments()
        self.args = self.parser.parse_args(namespace=self)

    def login(self):
        print("Username " + self.username)
        payload = {'username': self.username, 'password': self.password}
        url = self.app_base_url + "/admin/login"
        resp = requests.post(url, data=payload)
        resp = resp.json()
        result = resp['result'][0]
        print(resp)
        if resp:
            #verify that it's a succesful login
            assert resp['status'] == 'success'
            if 'sessionid' in result.keys():
                self.session_id = result['sessionid']
                print("Going to write sessionid in file")
                session_file = open(self.session_file_path, mode='w', encoding='utf-8')
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%m")
                session_file.write(self.session_id + "====" + timestamp)
                session_file.close()
            else:
                raise Exception("Didn't receive session-id after login")
        return resp['result']


    def add_arguments(self):
        """
        Entrypoint for subclasses to add arguments
        """
        pass

    def is_session_valid(self):
        self.get_sessionid()
        print("Session id= " + self.session_id)
        print("Timestamp= " + self.session_timestamp)
        timestamp = datetime.strptime(self.session_timestamp, '%Y-%m-%d %H:%M')
        now = datetime.now()
        delta = now - timestamp
        secs_in_one_hour = 60 * 60
        return delta.total_seconds() < secs_in_one_hour

    def get_sessionid(self):
        session_file = None 
        try:
            session_file = open(self.session_file_path, encoding='utf-8')
        except IOError:
            self.session_id = None
        else:
            token = session_file.read()
            splitter = "===="
            if splitter in token:
                self.session_id = token.split(splitter)[0]
                self.session_timestamp = token.split(splitter)[1]
            else:
                self.session_id = token
                self.session_timestamp = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
                session_file.close()


# = BaseCommand()
#.create_parser()
#rint b.session_id
#rint type(b.args)
#rint b.execute()
