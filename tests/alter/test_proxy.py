
from pylib.alter.proxy import Proxy


class Tester:
    """TestCase for Proxy."""

    @staticmethod
    def test_http_proxy() -> None:
        """Test http proxy parsing."""
        url = "http://hello_:World8@127.0.0.1:5000"
        proxy = Proxy.load(url=url)
        assert isinstance(proxy, Proxy)
        assert proxy.rdns is True
        assert proxy.scheme == "http"
        assert proxy.type == 3
        assert proxy.usr == "hello_"
        assert proxy.pwd == "World8"
        assert proxy.addr == "127.0.0.1"
        assert proxy.port == 5000
        assert proxy.url.startswith("http")
        assert proxy.server == "http://127.0.0.1:5000"
        assert isinstance(proxy.data, dict)
        assert list(proxy.data.keys()) == ["http", "https"]

        usr, pwd = "hello", "world"
        key, value = Proxy.header_auth(usr=usr, pwd=pwd)
        assert key and key.startswith("Proxy")
        assert value and value.startswith("Basic")

        key, value = proxy.auth
        assert key.startswith("Proxy")
        assert value.startswith("Basic")

    @staticmethod
    def test_socks5_proxy() -> None:
        """Test socks5 proxy parsing."""
        url = "socks5://hello_:World8@127.0.0.1:5000"
        proxy = Proxy.load(url=url)
        assert proxy.scheme == "socks5"
        assert proxy.type == 2

    @staticmethod
    def test_socks4_proxy() -> None:
        """Test socks4 proxy parsing."""
        url = "socks4://hello_:World8@127.0.0.1:5000"
        proxy = Proxy.load(url=url)
        assert proxy.scheme == "socks4"
        assert proxy.type == 1
