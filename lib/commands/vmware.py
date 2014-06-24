from commands.base import BaseCommand

class VMWareBase(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(args, kwargs)
        self.vm_username = self.cfg_parser('vmware', 'username')
        self.vm_password = self.cfg_parser('vmware', 'password')

    def add_arguments(self):
        self.parser.add_arguments('--email', help="Email of admin")
        self.parser.add_arguments('--vm_username', help='VMware username',\
                default=self.vm_username)
        self.parser.add_arguments('--vm_password', help='VMware password',\
                default=self.vm_password)


class VM(VMWareBase):
    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(args, kwargs)

    def add_arguments(self):
        super(VM, self).add_arguments()
        self.parser.add_arguments('--vm', help='Information about virtual machine')
        self.parser.add_arguments('--clone', help='Clones a machine from the moref, will have further options or maybe its own endpoint')
        self.parser.add_arguments('--delete', help='Deletes the machine')

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







a = Admin()
a.create_parser()
print a.args
