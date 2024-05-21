from pathlib import Path

from pylib.client.https.basic import AsyncHTTPBasic, HTTPBasic

from .test_abs import AbsTester


class TesterBasic(AbsTester):
    """Test HTTP Basic Client.

    Notes:
        - Test Headers
        - Test Cookies
        - Test Request Methods
        - Test Impesonate
        - Test Proxy

    """

    def test_headers(self) -> None:
        """Test header operation."""
        http = HTTPBasic(
            proxy_url=self.proxy_socks,
        )
        key, value = "Hello", "World"

        http.header_set(key=key, value=value)
        assert http.header_get(key=key) == value

        # test other common headers
        print(http._session.headers)
        http.set_hd_accept(value=value)
        print(http._session.headers)
        assert http.header_get("accept") == value

        http.set_hd_accept_encoding(value=value)
        assert http.header_get("accept-encoding") == value

        http.set_hd_accept_lang(value=value)
        assert http.header_get("accept-language") == value

        http.set_hd_origin(value=value)
        assert http.header_get("origin") == value

        http.set_hd_referer(value=value)
        assert http.header_get("referer") == value

        http.set_hd_content_type(value=value)
        assert http.header_get("content-Type") == value

        http.set_hd_ajax(value=value)
        assert http.header_get("X-Requested-With") == value

        http.set_hd_form_data()
        value_data = "application/x-www-form-urlencoded; charset=UTF-8"
        assert http.header_get("Content-Type") == value_data

        http.set_hd_json_payload()
        value_json = "application/json; charset=UTF-8"
        assert http.header_get("Content-Type") == value_json

    def test_cookies(self, tmp_path: Path) -> None:
        """Test session cookies operation."""
        file_cookie = tmp_path / "http.cookie.json"

        http = HTTPBasic(
            proxy_url=self.proxy_socks,
        )

        key, value = "hello", "world"
        http.cookie_set(key=key, value=value)
        http.cookie_save(file_cookie=file_cookie)

        http.cookie_set(key=key, value=None)
        assert http.cookie_get(key=key) is None

        assert file_cookie.is_file()

        http.cookie_load(file_cookie=file_cookie)
        assert http.cookie_get(key=key) == value

    def test_requests(self) -> None:
        """Test request method.

        Issues:
            - curl_cffi does NOT support response mock
            - httpbin.org only supports Methods: GET, POST, DELETE, PATCH, PUT

        """
        http = HTTPBasic(
            proxy_url=self.proxy_socks,
        )

        # GET Method
        response = http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        # POST Method
        payload: dict = {"hello": "world"}
        response = http.post(url=self.url_post, json=payload)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["json"] == payload

        # DELETE Method
        response = http.delete(url=self.url_delete)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_delete

        # PATCH Method
        response = http.patch(url=self.url_patch)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_patch

        # PUT Method
        response = http.put(url=self.url_put)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_put

    def test_proxy(self) -> None:
        """Test Proxy."""
        http = HTTPBasic(
            proxy_url=self.proxy_socks,
        )

        # GET Method
        response = http.get(url=self.url_ip, debug=True)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["origin"]  # in proxy_url

    def test_impersonate(self) -> None:
        """Test Impersonate.

        Issues:
            - ja3_hash not same as the official curl_cffi libaray tests, need to find out WHY...

        """
        JA3_URL = "https://tls.browserleaks.com/json"
        # Copied from my browser on macOS
        # CHROME_JA3_HASH = "53ff64ddf993ca882b70e1c82af5da49"
        # Edge 101 is the same as Chrome 101
        # EDGE_JA3_HASH = "53ff64ddf993ca882b70e1c82af5da49"
        # Same as safari 16.x
        # SAFARI_JA3_HASH = "8468a1ef6cb71b13e1eef8eadf786f7d"

        browser = HTTPBasic(
            impersonate="chrome101",
            proxy_url=self.proxy_socks,
        )
        response = browser.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Chrome/101.0" in response.json()["user_agent"]

        browser = HTTPBasic(
            impersonate="edge101",
            proxy_url=self.proxy_socks,
        )
        response = browser.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Edg/101.0" in response.json()["user_agent"]

        browser = HTTPBasic(
            impersonate="safari15_5",
            proxy_url=self.proxy_socks,
        )
        response = browser.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Version/15.5 Safari" in response.json()["user_agent"]


class TesterAsyncBasic(AbsTester):
    """Tester for AsyncBasic."""

    def test_headers(self) -> None:
        """Test header operations."""
        key, value = "Hello", "World"

        http = AsyncHTTPBasic(
            proxy_url=self.proxy_socks,
        )
        # print(http._session.headers)
        http.header_set(key=key, value=value)
        # print(http._session.headers)
        assert http.header_get(key=key) == value

        # test other common headers
        http.set_hd_accept(value=value)
        assert http.header_get("accept") == value

        http.set_hd_accept_encoding(value=value)
        assert http.header_get("accept-encoding") == value

        http.set_hd_accept_lang(value=value)
        assert http.header_get("accept-language") == value

        http.set_hd_origin(value=value)
        assert http.header_get("origin") == value

        http.set_hd_referer(value=value)
        assert http.header_get("referer") == value

        http.set_hd_content_type(value=value)
        assert http.header_get("content-Type") == value

        http.set_hd_ajax(value=value)
        assert http.header_get("X-Requested-With") == value

        http.set_hd_form_data()
        value_data = "application/x-www-form-urlencoded; charset=UTF-8"
        assert http.header_get("Content-Type") == value_data

        http.set_hd_json_payload()
        value_json = "application/json; charset=UTF-8"
        assert http.header_get("Content-Type") == value_json

    def test_cookies(self, tmp_path: Path) -> None:
        """Test session cookie operations."""
        file_cookie = tmp_path / "http.cookie.json"

        http = AsyncHTTPBasic(
            proxy_url=self.proxy_socks,
        )

        key, value = "hello", "world"
        http.cookie_set(key=key, value=value)
        http.cookie_save(file_cookie=file_cookie)

        http.cookie_set(key=key, value=None)
        assert http.cookie_get(key=key) is None

        assert file_cookie.is_file()

        http.cookie_load(file_cookie=file_cookie)
        assert http.cookie_get(key=key) == value

    async def test_requests(self) -> None:
        """Test request methods.
        
        # HEAD Method not tested.
        # CONNECT Method not tested.
        # OPTIONS Method not tested.
        
        """

        http = AsyncHTTPBasic(
            proxy_url=self.proxy_socks,
        )

        # GET Method
        response = await http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        # POST Method
        payload: dict = {"hello": "world"}
        response = await http.post(url=self.url_post, json=payload)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["json"] == payload

        # DELETE Method
        response = await http.delete(url=self.url_delete)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_delete

        # PATCH Method
        response = await http.patch(url=self.url_patch)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_patch

        # PUT Method
        response = await http.put(url=self.url_put)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_put

        await http._session.close()

    async def test_impersonate(self) -> None:
        """Test Impersonate.

        Issues:
            - ja3_hash not same as the official curl_cffi libaray tests, need to find out WHY...

        """
        JA3_URL = "https://tls.browserleaks.com/json"
        # Copied from my browser on macOS
        # CHROME_JA3_HASH = "53ff64ddf993ca882b70e1c82af5da49"
        # Edge 101 is the same as Chrome 101
        # EDGE_JA3_HASH = "53ff64ddf993ca882b70e1c82af5da49"
        # Same as safari 16.x
        # SAFARI_JA3_HASH = "8468a1ef6cb71b13e1eef8eadf786f7d"

        http = AsyncHTTPBasic(
            impersonate="chrome101",
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Chrome/101.0" in response.json()["user_agent"]

        await http._session.close()

        http = AsyncHTTPBasic(
            impersonate="edge101",
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Edg/101.0" in response.json()["user_agent"]

        await http._session.close()

        http = AsyncHTTPBasic(
            impersonate="safari15_5",
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=JA3_URL, debug=True)
        assert response is not None
        assert response.status_code == 200
        # print(response.text)
        assert "Version/15.5 Safari" in response.json()["user_agent"]
        await http._session.close()

    async def test_proxy(self) -> None:
        """Test Proxy."""
        http = AsyncHTTPBasic(
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=self.url_ip, debug=True)
        assert response is not None
        assert response.status_code == 200
        print(response.text)
        assert response.json()["origin"] # in proxy_url

        await http._session.close()
