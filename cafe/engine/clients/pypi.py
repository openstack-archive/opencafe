try:
     import xmlrpclib
except ImportError:
     import xmlrpc.client as xmlrpclib


class PyPIClient(object):
    PLUGIN_HEADER = "cafe-plugin-"
    def __init__(self, url="https://pypi.python.org/pypi"):
        self.rpc_client = xmlrpclib.ServerProxy(url)

    def list_plugins(self):
        plugins = []
        # search call is broken in pypi with tons of bugs open for the issue
        for name in self.rpc_client.list_packages():
            name = self.get_plugin_name(name)
            if name is not None:
                plugins.append(name)
        return sorted(list(set(plugins)))

    @classmethod
    def get_package_name(cls, name):
        return "{0}{1}".format(cls.PLUGIN_HEADER, name)

    @classmethod
    def get_plugin_name(cls, package_name):
        if package_name.startswith(cls.PLUGIN_HEADER):
            return package_name[len(cls.PLUGIN_HEADER):]
        return None
