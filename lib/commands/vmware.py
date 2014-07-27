import requests
from base import BaseCommand
from configparser import SafeConfigParser


class VMWareBase(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(VMWareBase, self).__init__(args, kwargs)
        self.vcenter_username = self.cfg_parser.get('vmware', 'username')
        self.vcenter_password = self.cfg_parser.get('vmware', 'password')
        self.vcenter_url = self.cfg_parser.get('vmware', 'vcenter_url')
        self.url = self.app_base_url + '/vmware'

    def add_argument(self):
        self.parser.add_argument('--email', help="Email of admin")
        self.parser.add_argument('--vcenter_username', help='VMware username',\
                default=self.vcenter_username)
        self.parser.add_argument('--vcenter_password', help='VMware password',\
                default=self.vcenter_password)
        self.parser.add_argument('--vcenter_hrl', help='Vcenter URL')

    def vm_login(self):
        """
        By default 'vcenter_username' and 'vcenter_password' are taken
        from the config file, however, they can be specified on 
        command line as well
        Usage:
        >> python vmware.py --endpoint vm_login --vcenter_username username --vcenter_passowrd pwd
            --vcenter_url http://10.10.16.21/sdk
        """
        print("Session= " + self.session_id)
        if not self.session_id:
            self.login()
        assert self.session_id is not None
        payload = {'vcenter_username':self.vcenter_username, 'vcenter_password':\
                self.vcenter_password, 'vcenter_url': self.vcenter_url}
        url = self.url + "/-/" + self.session_id
        print('Requesting ' + url)
        print("Data= " + str(payload))
        resp = requests.post(url, data=payload)
        resp = resp.json()
        print(resp)
        rows = [0]
        assert resp['result'] == 'success'
        return resp, rows, resp.keys()


class VM(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(args, kwargs)
        #these will be populated by ArgumentParser
        self.vmname = None
        self.attr = None
        self.attr_key = None
        self.attr_value = None

    def add_argument(self):
        super(VM, self).add_argument()
        self.parser.add_argument('--vm', help='Information about virtual machine')
        self.parser.add_argument('--clone', help='Clones a machine from the moref, will have further options or maybe its own endpoint')
        self.parser.add_argument('--delete', help='Deletes the machine')
        self.parser.add_argument('--vmname', help='Name of one VM')
        self.parser.add_argument('--attr', help='If you want to know an attribute of VM then use this argument')
        self.parser.add_argument("--attr_key", help='This is attribute key e.g. one possible value can be "memorymb"')
        self.parser.add_argument("--attr_value", help='Attribute value e.g. one possible value can be "4097" assuming' + \
                "attr_key was 'memorymb'")
    def execute(self):
        self.create_parser()
        if not self.endpoint:
            raise Exception("An endpoint must be defined")
        try:
            method = getattr(self, self.endpoint)
            r, rows, keys = method() #call the method specified in self.endpoint
            if self.csv:
                print(self.to_csv(r, rows, keys))
        except AttributeError as e:
            print(e)
            print("Please enter a correct REST endpoint")

    def verify_login(self):
        if not self.session_id:
            print("Wait, trying to login first...")
            self.vm_login()
    def get_all_vms_info(self):
        """
        Usage:
        >> python vmware.py --endpoint get_all_vms_info
        """
        self.verify_login()
        assert self.session_id is not None
        print('Request ' + self.url + "/vm/-/" + self.session_id)
        resp = requests.get(self.url + "/vm/-/" + self.session_id).json()
        print(resp)
        return resp, None, resp.keys()

    def get_one_vm_info(self):
        """
        Usage:
        >> python vmware.py --endpoint get_one_vm --vmname vm-32
        """
        self.verify_login()
        assert self.session_id is not None
        assert self.vmname is not None
        url = self.url + "/vm/" + self.vmname + "/-/" + self.session_id
        print('Requesitng ' + url)
        resp = requests.get(url).json()
        print(resp)
        return resp, None, resp.keys()

    def get_vm_attribute(self):
        """
        Usage:
        >> python vmware.py --endpoint get_vm_attribute --vmname vm-32 --attr memory
        """
        self.verify_login()
        assert self.session_id is not None
        assert self.attr is not None
        assert self.vmname is not None
        url = self.url + "/vm/" + self.vmname + "/" + self.attr + "/-/" + self.session_id
        print("Requesting " + url)
        resp = requests.get(url).json()
        assert resp['result'] == 'success'
        print(resp)
        return resp

    def change_vm_attribute(self):
        """
        Usage:
        >> python vmware.py --endpoint change_vm_attribute --vmname vm-32
            --attr memory --attr_key memorymb --attr_value 2097
        """
        self.verify_login()
        assert self.session_id is not None
        assert self.attr is not None
        assert self.vmname is not None
        assert self.attr_value is not None
        #e.g. self.attr can be 'memory' whereas self.attr_key can be 'memorymb'
        #and self.attr_value can be '4097
        payload = { self.attr_key : self.attr_value }
        url = self.url + "/vm/" + self.vmname + "/" + self.attr + "/-/" + self.session_id
        print("Requesting " + url)
        print("Sending data " + str(payload))
        resp = requests.put(url, data=payload).json()
        assert resp['result'] == 'success'
        print(resp)
        return resp




    

class Task(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(args, kwargs)

    def add_argument(self):
        super(Task, self).add_argument()
        self.parser.add_argument('--taskname')

class Network(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(args, kwargs)

    def add_argument(self):
        super(Network, self).add_argument()
        self.parser.add_argument('--moref')

class Folder(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Folder, self).__init__(args, kwargs)

    def add_argument(self):
        super(Folder, self).add_argument()
        self.parser.add_argument('--moref', help='Information about specific folder')
        self.parser.add_argument('--create', help='Creates a folder in the root folder, if moref is given then in the requested folder')
        self.parser.add_argument('--delete', help='moref needs to be given and it deletes the folder')
        self.parser.add_argument('--modify', help='Placeholder for later maybe it will get an own endpoint')


class ResourcePool(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(ResourcePool, self).__init__(args, kwargs)

    def add_argument(self):
        super(ResourcePool, self).add_argument()
        self.parser.add_argument('--moref', help='Information about specific resourcepool')
        self.parser.add_argument('--create', help='Create resourcepool in root folder, or if moref given then in resourcepool')
        self.parser.add_argument('--delete', help='moref needs to be given, and it deletes the resourcepool')
        self.parser.add_argument('--modify', help='Placeholder for later maybe it will get an own endpoint')





if __name__ == "__main__":
    vm = VM()
    vm.execute()
