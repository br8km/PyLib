#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Proxy cls for http/socks proxy."""


from base64 import encodebytes
from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import unquote_to_bytes

import regex as re

__all__ = ("Proxy",)


@dataclass
class Proxy:
    """Proxy."""

    addr: str = ""
    port: int = 80
    usr: str = ""
    pwd: str = ""

    scheme: str = "http"
    type: int = 3
    rdns: bool = True

    @classmethod
    def load(cls, url: str, rdns: bool = True) -> "Proxy":
        """Load Proxy by parsing proxy_str.

        Parameters:
            - proxy_url: str, format: `usr:pwd@addr:port` or `addr:port` or `http://...`
            - rdns: bool, reverse dns, default True
        """
        scheme = url.split("://")[0] if "://" in url else "http"
        scheme = scheme.lower()

        data_type = {
            "http": 3,
            "socks5": 2,
            "socks4": 1,
        }

        if scheme not in data_type.keys():
            raise ValueError(f"proxy type not supported: `{scheme}`!")

        proxy_type = data_type.get(scheme) or 3
        addr, port, usr, pwd = "", 80, "", ""

        # long proxy format: usr:pwd@addr:port
        pattern_long = r"([\w]+?):([\w]+?)@([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}):([\d]{2,5})"
        # short proxy format: addr:port
        pattern_short = r"([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}):([\d]{2,5})"

        if "@" in url:
            found = re.compile(pattern_long, re.I).findall(url)
            if found:
                usr, pwd, addr, port = found[0]
                if cls.valid(addr):
                    port = int(port)
                    return cls(
                        addr=addr,
                        port=port,
                        usr=usr,
                        pwd=pwd,
                        scheme=scheme,
                        rdns=rdns,
                        type=proxy_type,
                    )

        found = re.compile(pattern_short, re.I).findall(url)
        if found:
            addr, port = found[0]
            if cls.valid(addr):
                port = int(port)
                return cls(
                    addr=addr,
                    port=port,
                    usr=usr,
                    pwd=pwd,
                    scheme=scheme,
                    rdns=rdns,
                    type=proxy_type,
                )

        raise ValueError(f"bad proxy format: {url}")

    @property
    def server(self) -> str:
        """Get proxy server address without auth."""
        return f"{self.scheme}://{self.addr}:{self.port}"

    @property
    def url(self) -> str:
        """Get proxy url string."""
        if self.usr and self.pwd:
            return f"{self.scheme}://{self.usr}:{self.pwd}@{self.addr}:{self.port}"
        return self.server

    @property
    def data(self) -> dict[str, str]:
        """to proxy data dictionary."""
        return {"http": self.url, "https": self.url}

    @classmethod
    def header_auth(cls, usr: str, pwd: str) -> tuple[str, str]:
        """Generate proxy header value for `Proxy-Authorization`."""
        if usr and pwd:
            auth_str = f"{usr}:{pwd}"
            auth_bytes = unquote_to_bytes(auth_str)
            auth_str = encodebytes(auth_bytes).decode("utf-8")
            auth_str = "".join(auth_str.split())  # get rid of whitespace
            return "Proxy-Authorization", "Basic " + auth_str

        raise ValueError(f"proxy auth error @ usr=`{usr}`, pwd=`{pwd}`")

    @property
    def auth(self) -> tuple[str, str]:
        """Get header auth string tuple."""
        return self.header_auth(usr=self.usr, pwd=self.pwd)

    @classmethod
    def valid(cls, addr: str) -> bool:
        """validation for ip address"""
        try:
            ip_address(addr)
            return True
        except ValueError:
            return False

