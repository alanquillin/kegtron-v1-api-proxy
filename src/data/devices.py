DEVICES = {}


def exists(id):
    return id in DEVICES.keys()

def get(id):
    return DEVICES.get(id)

def list():
    return DEVICES

def create(id, data):
    DEVICES[id] = data
    return data

def update(id, data):
    _d = DEVICES.get(id)

    if not _d:
        _d = data
    else:
        _d.update(data)
    
    DEVICES[id] = _d
    return _d
