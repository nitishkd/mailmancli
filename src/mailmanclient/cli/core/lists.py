from mailmanclient import Client


class Lists():

    """Mailing list related actions."""

    def connect(self, host, port, username, password):
        self.client = Client('%s:%s/3.0' % (host, port), username, password)

        # Test if connection OK else raise exception
        lists = self.client.lists

    def create(self, domain_name, list_name):
        """Create a mailing list with specified list_name
           in the domain specified by domain_name.

           :param domain_name: string Name of the domain
           :param list_name: string Name of the list
        """

        if domain_name is None or list_name is None:
            print 'Specify domain name and list name'
            exit(1)
        try:
            domain = self.client.get_domain(domain_name)
        except Exception:
            print 'Domain not found'
            exit(1)
        try:
            domain.create_list(list_name)
        except Exception:
            print 'Mailing list already exists'

    def delete(self, list_name):
        pass

    def list(self, domain_name, list_name):
        pass

    def list_members(self, list_name):
        pass
