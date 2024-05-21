from pathlib import Path

from pylib.client.http.basic import HTTPBasic

from .test_abs import AbsTester


class TesterBasic(AbsTester):
    """Test HTTP Basic Client."""

    def test_headers(self) -> None:
        """Test header operations."""
        http = HTTPBasic(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
        )

        key, value = "hello", "world"

        http.header_set(key=key, value=value)
        assert http.header_get(key=key) == value

        http.set_hd_accept(value=value)
        assert http.header_get("Accept") == value

        http.set_hd_accept_encoding(value=value)
        assert http.header_get("Accept-Encoding") == value

        http.set_hd_accept_lang(value=value)
        assert http.header_get("Accept-Language") == value

        http.set_hd_origin(value=value)
        assert http.header_get("Origin") == value

        http.set_hd_referer(value=value)
        assert http.header_get("Referer") == value

        http.set_hd_content_type(value=value)
        assert http.header_get("Content-Type") == value

        http.set_hd_ajax(value=value)
        assert http.header_get("X-Requested-With") == value

        http.set_hd_form_data()
        value_data = "application/x-www-form-urlencoded; charset=UTF-8"
        assert http.header_get("Content-Type") == value_data

        http.set_hd_json_payload()
        value_json = "application/json; charset=UTF-8"
        assert http.header_get("Content-Type") == value_json

    def test_cookies(self, tmp_path: Path) -> None:
        """Test cookie operations."""
        file_cookie = tmp_path / "http.cookie.json"
        file_cookie.unlink(missing_ok=True)

        http = HTTPBasic(
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

    def test_requests(self) -> None:
        """Test request methods.
        
        # HEAD Method not tested.
        # CONNECT Method not tested.
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
