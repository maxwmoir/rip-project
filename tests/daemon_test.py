
from src.daemon import Daemon

def test_square():

    id = "2"
    config = "./test"
    daemon = Daemon(id, config)
    assert daemon.id == "2" 