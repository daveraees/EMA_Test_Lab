# this module maintains the list of activated devices used for measurements

class ListOfDevices:
    """Maintain the dynamically actualized list of activated devices"""
    def __init__(self):
        self.seznam = []
        return
    def append(self, device):
        self.seznam.append(device)
        return len(self.seznam)
    def list(self):
        return self.seznam

