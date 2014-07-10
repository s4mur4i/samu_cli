from base import BaseCommand

class VMWareBase(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(VMWareBase, self).__init__(args, kwargs)
        self.vcenter_username = self.cfg_parser('vmware', 'username')
        self.vcenter_password = self.cfg_parser('vmware', 'password')
        self.url = self.app_base_url + '/vmware'

    def add_arguments(self):
        self.parser.add_arguments('--email', help="Email of admin")
        self.parser.add_arguments('--vcenter_username', help='VMware username',\
                default=self.vcenter_username)
        self.parser.add_arguments('--vcenter_password', help='VMware password',\
                default=self.vcenter_password)
        self.parser.add_arguments('--vcenter_hrl', help='Vcenter URL')

    def vm_login(self):
        assert self.session_id is not None
        payload = {'vcenter_username':self.vcenter_username, 'vcenter_password':\
                self.vcenter_password, 'vcenter_url': self.vcenter_url}
        resp = requests.post(self.url + "/-/" + self.session_id, data=payload)
        resp = resp.json()
        print(resp)
        assert resp['result'] == 'success'
        return resp 


class VM(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(args, kwargs)

    def add_arguments(self):
        super(VM, self).add_arguments()
        self.parser.add_arguments('--vm', help='Information about virtual machine')
        self.parser.add_arguments('--clone', help='Clones a machine from the moref, will have further options or maybe its own endpoint')
        self.parser.add_arguments('--delete', help='Deletes the machine')
        self.parser.add_arguments('--vmname', help='Name of one VM')
        self.parser.add_arguments('--attr', help='If you want to know an attribute of VM then use this argument')
        self.parser.add_arguments("--attr_key", help='This is attribute key e.g. one possible value can be "memorymb"')
        self.parser.add_arguments("--attr_value", help='Attribute value e.g. one possible value can be "4097" assuming' + \
                "attr_key was 'memorymb'")
    
    def get_all_vms_info(self):
        assert self.session_id is not None
        resp = requests.get(self.url + "/vm/-/" + self.session_id).json()
        print(resp)
        return resp

    def get_one_vm_info(self):
        assert self.session_id is not None
        assert self.vmname is not None
        resp = requests.get(self.url + "/vm/" + self.vmname + "-/" + self.session_id).json()
        print(resp)
        return resp

    def get_vm_attribute(self):
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
        assert self.session_id is not None
        assert self.attr is not None
        assert self.vmname is not None
        assert self.attr_value is not None
        #e.g. self.attr can be 'memory' whereas self.attr_key can be 'memorymb'
        #and self.attr_value can be '4097
        data = { self.attr_key : self.attr_value }
        url = self.url + "/vm/" + self.vmname + "/" + self.attr + "/-/" + self.session_id
        print("Requesting " + url)
        resp = requests.get(url).json()
        assert resp['result'] == 'success'
        print(resp)
        return resp




    

class Task(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(args, kwargs)

    def add_arguments(self):
        super(Task, self).add_arguments()
        self.parser.add_arguments('--taskname')

class Network(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(args, kwargs)

    def add_arguments(self):
        super(Network, self).add_arguments()
        self.parser.add_arguments('--moref')

class Folder(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(Folder, self).__init__(args, kwargs)

    def add_arguments(self):
        super(Folder, self).add_arguments()
        self.parser.add_arguments('--moref', help='Information about specific folder')
        self.parser.add_arguments('--create', help='Creates a folder in the root folder, if moref is given then in the requested folder')
        self.parser.add_arguments('--delete', help='moref needs to be given and it deletes the folder')
        self.parser.add_arguments('--modify', help='Placeholder for later maybe it will get an own endpoint')


class ResourcePool(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(ResourcePool, self).__init__(args, kwargs)

    def add_arguments(self):
        super(ResourcePool, self).add_arguments()
        self.parser.add_arguments('--moref', help='Information about specific resourcepool')
        self.parser.add_arguments('--create', help='Create resourcepool in root folder, or if moref given then in resourcepool')
        self.parser.add_arguments('--delete', help='moref needs to be given, and it deletes the resourcepool')
        self.parser.add_arguments('--modify', help='Placeholder for later maybe it will get an own endpoint')





if __name__ == "__main__":
    vm = VM()
    vm.execute()
