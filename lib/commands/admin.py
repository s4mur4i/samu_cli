from base import BaseCommand

class Admin(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(args, kwargs)
        
    def add_arguments(self):
        self.parser.add_argument('--email', help="Email of admin")


a = Admin()
a.create_parser()
print a.args
