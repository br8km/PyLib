from pathlib import Path

from pylib.client.http2.basic import AsyncHTTPBasic, HTTPBasic
from .test_abs import AbsTester


class TesterBasic(AbsTester):
    """Test HTTP Basic Client.

    Warnings:
        # Method NOT tested @ 20240521:
            - `connect`, `head`, `options`

    """

    def test_http_version(self) -> None:
        """Test HTTP2/HTTP1 version."""
        # test http/1
        http_1 = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            http2=False,
        )
        response = http_1.get(url=self.url_headers, debug=True)
        assert response is not None
        assert response.status_code == 200

        # test http/2
        http_2 = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            http2=True,
        )
        response = http_2.get(url=self.url_headers, debug=True)
        assert response is not None
        assert response.status_code == 200

    def test_useragent(self) -> None:
        """Test User-Agent."""
        http = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )
        response = http.get(url=self.url_headers, debug=True)
        assert response is not None
        assert response.status_code == 200
        print(response.text)
        headers = response.json()["headers"]
        assert headers.get("User-Agent") == http._user_agent

    def test_proxy(self) -> None:
        """Test Proxy."""
        http = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )
        response = http.get(url=self.url_ip, debug=True)
        assert response is not None
        assert response.status_code == 200
        print(response.text)
        assert response.json()["origin"]  # in proxy_url

    def test_headers(self) -> None:
        """Test headers operation."""
        http = HTTPBasic(
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
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
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
        )
        key, value = "hello", "world"
        http.cookie_set(key=key, value=value)
        http.cookie_save(file_cookie=file_cookie)

        http.cookie_set(key=key, value=None)
        assert http.cookie_get(key=key) is None

        assert file_cookie.is_file()

        http.cookie_load(file_cookie=file_cookie)
        assert http.cookie_get(key=key) == value

        file_cookie.unlink(missing_ok=True)

    def test_requests(self) -> None:
        """Test request methods.
        
        # HEAD Method not tested.
        # OPTIONS Method not tested.
        
        """

        http = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )

        # check `User-Agent` header with response
        response = http.get(self.url_headers)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["headers"]["User-Agent"] == self.user_agent

        # GET Method
        response = http.get(self.url_get)
        assert response is not None
        assert response.status_code == 200

        # POST Method
        response = http.post(url=self.url_post)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_post

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


class TesterAsyncBasic(AbsTester):
    """Tester for AsyncBasic.

    Warnings:
        # CONNECT Method: NO testing method @ 20240521

    """

    async def test_http_version(self) -> None:
        """Test HTTP2/HTTP1 version."""
        # test http/1
        http_1 = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            http2=False,
        )
        response = await http_1.get(url=self.url_headers)
        assert response is not None
        assert response.status_code == 200

        await http_1._session.aclose()

        # test http/2
        http_2 = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            http2=True,
        )
        response = await http_2.get(url=self.url_headers)
        assert response is not None
        assert response.status_code == 200

        await http_2._session.aclose()

    async def test_useragent(self) -> None:
        """Test User-Agent."""
        http = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=self.url_headers)
        assert response is not None
        assert response.status_code == 200
        print(response.text)
        headers = response.json()["headers"]
        assert headers.get("User-Agent") == http._user_agent

        await http._session.aclose()

    async def test_proxy(self) -> None:
        """Test Proxy."""
        http = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )
        response = await http.get(url=self.url_ip)
        assert response is not None
        assert response.status_code == 200
        print(response.text)
        assert response.json()["origin"]  # in proxy_url

        await http._session.aclose()

    async def test_headers(self) -> None:
        """Test header operation."""
        http = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )

        key, value = "Hello", "World"
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

        await http._session.aclose()

    async def test_cookies(self, tmp_path: Path) -> None:
        """Test session cookies operation."""
        file_cookie = tmp_path / "http.cookie.json"

        http = AsyncHTTPBasic(
            user_agent=self.user_agent,
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

        file_cookie.unlink(missing_ok=True)

        await http._session.aclose()

    async def test_requests(self) -> None:
        """Test request method.
        
        # HEAD Method not tested.
        # OPTIONS Method not tested.
        
        """
        http = AsyncHTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )

        # check `User-Agent` header with response
        response = await http.get(self.url_headers)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["headers"]["User-Agent"] == self.user_agent

        # GET Method
        response = await http.get(self.url_get)
        assert response is not None
        assert response.status_code == 200

        # POST Method
        response = await http.post(url=self.url_post)
        assert response is not None
        assert response.status_code == 200
        assert response.json()["url"] == self.url_post

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

        await http._session.aclose()
