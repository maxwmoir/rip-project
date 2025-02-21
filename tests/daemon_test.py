
from src.daemon import Daemon

def test_square():

    id = "id1"
    config = './tests/cfgs/cfg1.txt'
    daemon = Daemon(id, config)
    daemon.print_info()
    assert daemon.id == 1 
    assert len(daemon.socks) == 3