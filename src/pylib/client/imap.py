"""Imap Client."""

import imaplib
import random
import ssl
import time
from email import message_from_bytes, message_from_string
from email.header import decode_header
from email.message import Message
from email.utils import parseaddr, parsedate_to_datetime
from typing import Any, Optional, Union

import arrow
import regex as re
import socks
from regex import Pattern

from ..alter.proxy import Proxy
from ..utils.debugger import Debugger


__all__ = ("ImapClient",)


class SocksIMAP4(imaplib.IMAP4):
    """
    IMAP Service through socks proxy
    Note: PySocks(socks) lib required.
    """

    PROXY_TYPES = {
        "socks4": socks.PROXY_TYPE_SOCKS4,
        "socks5": socks.PROXY_TYPE_SOCKS5,
        "http": socks.PROXY_TYPE_HTTP,
    }

    def __init__(
        self,
        host: str,
        port: int = imaplib.IMAP4_PORT,  # type: ignore
        proxy_addr: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        proxy_type: Optional[int] = None,
        proxy_rdns: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_type = proxy_type
        self.proxy_rdns = proxy_rdns

        imaplib.IMAP4.__init__(self, host, port)

    def _create_socket(self, timeout: Optional[int] = None) -> Any:
        """create socket"""
        return socks.create_connection(
            (self.host, self.port),
            timeout=timeout,
            proxy_type=self.proxy_type,
            proxy_addr=self.proxy_addr,
            proxy_port=self.proxy_port,
            proxy_rdns=self.proxy_rdns,
            proxy_username=self.proxy_username,
            proxy_password=self.proxy_password,
        )


class SocksIMAP4SSL(SocksIMAP4):
    # pylint: disable=too-many-arguments
    """Socks imaplib ssl version"""

    def __init__(
        self,
        host: str = "",
        port: int = imaplib.IMAP4_SSL_PORT,  # type: ignore
        keyfile: Any = None,
        certfile: Any = None,
        ssl_context: Any = None,
        proxy_addr: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        proxy_type: Optional[int] = None,
        proxy_rdns: bool = True,
    ) -> None:
        if ssl_context is not None:
            if keyfile is not None:
                msg = "arguments are mutually exclusive: ssl_context, keyfile"
                raise ValueError(msg)
            if certfile is not None:
                msg = "arguments are mutually exclusive: ssl_context, certfile"
                raise ValueError(msg)

        self.keyfile = keyfile
        self.certfile = certfile
        if ssl_context is None:
            ssl_context = ssl._create_unverified_context(
                certfile=certfile, keyfile=keyfile
            )  # type: ignore
        self.ssl_context = ssl_context

        SocksIMAP4.__init__(
            self,
            host=host,
            port=port,
            proxy_addr=proxy_addr,
            proxy_port=proxy_port,
            proxy_username=proxy_username,
            proxy_password=proxy_password,
            proxy_type=proxy_type,
            proxy_rdns=proxy_rdns,
        )

    def _create_socket(self, timeout: Optional[int] = None) -> Any:
        sock = SocksIMAP4._create_socket(self, timeout=timeout)
        server_host = self.host if ssl.HAS_SNI else None
        return self.ssl_context.wrap_socket(sock, server_hostname=server_host)

    def open(
        self,
        host: str = "",
        port: int = imaplib.IMAP4_PORT,  # type: ignore
        timeout: Optional[float] = None,
    ) -> Any:
        SocksIMAP4.open(self, host, port, timeout)


class ImapClient:
    """Imap Client"""

    __slots__ = (
        "_host",
        "_port",
        "_usr",
        "_pwd",
        "_ssl",
        "_demo",
        "_proxy",
        "_debugger",
        "_folders",
        "_conn",
        "_encoding",
    )

    def __init__(
        self,
        host: str,
        port: int,
        usr: str,
        pwd: str,
        ssl: bool = True,
        demo: bool = True,
        proxy: Optional[Proxy] = None,
        debugger: Optional[Debugger] = None,
        encoding: str = "unicode_escape",
    ) -> None:
        self._host = host
        self._port = port
        self._usr = usr
        self._pwd = pwd
        self._ssl = ssl
        self._demo = demo
        self._proxy = proxy
        self._debugger = debugger
        self._encoding = encoding

        self._folders = ["Inbox"]
        self._conn: Union[SocksIMAP4, SocksIMAP4SSL, None] = None

    def log(self, message: Any) -> None:
        """logging message if demo is True"""
        if self._demo is True:
            now = arrow.now().format("YYYY-MM-DD HH:mm:ss")
            print(f"{now} - {message}")

    def login(self) -> bool:
        """login using imaplib custom"""
        if self._proxy:
            if self._ssl:
                self._conn = SocksIMAP4SSL(
                    host=self._host,
                    port=self._port,
                    proxy_addr=self._proxy.addr,
                    proxy_port=self._proxy.port,
                    proxy_username=self._proxy.usr,
                    proxy_password=self._proxy.pwd,
                    proxy_type=self._proxy.type,
                    proxy_rdns=self._proxy.rdns,
                )
            else:
                self._conn = SocksIMAP4(
                    host=self._host,
                    port=self._port,
                    proxy_addr=self._proxy.addr,
                    proxy_port=self._proxy.port,
                    proxy_username=self._proxy.usr,
                    proxy_password=self._proxy.pwd,
                    proxy_type=self._proxy.type,
                    proxy_rdns=self._proxy.rdns,
                )
        else:
            if self._ssl:
                self._conn = imaplib.IMAP4_SSL(
                    host=self._host,
                    port=self._port,
                )
            else:
                self._conn = imaplib.IMAP4(
                    host=self._host,
                    port=self._port,
                )

        if self._demo is True:
            self._conn.debug = 4

        return bool(
            self._conn.login(
                user=self._usr,
                password=self._pwd,
            )
        )

    def logout(self) -> bool:
        """logout for imaplib"""
        if self._conn and self._conn.close():
            return bool(self._conn.lougout())
        return False

    @staticmethod
    def is_bytes(obj: Any) -> bool:
        """check is bytes or not"""
        try:
            obj.decode()
            return True
        except AttributeError:
            return False

    def _to_str(self, obj: Union[str, bytes]) -> str:
        """ensure bytes to be string"""
        if isinstance(obj, bytes):
            return obj.decode(encoding=self._encoding, errors="ignore")
        return obj

    @staticmethod
    def guess_charset(msg: Message) -> str:
        """guess charset for email message"""
        charset = ""
        guess = msg.get_charsets()
        if guess is None:
            content_type = msg.get("Content-Type") or ""
            content_type = content_type.lower().replace('"', "")
            pattern = re.compile(r"(?<=charset=)[\w\-]+")
            result = pattern.search(content_type)
            if result:
                charset = result.group()
        return charset

    def get_uids(self, folder: str, query: str) -> list[str]:
        """search to get list of email uids"""
        if self._conn:
            flag, data = self._conn.select(folder)
            if flag == "OK":
                time.sleep(random.uniform(0.05, 0.10))
                flag, data = self._conn.search(None, query)
                if flag == "OK":
                    return [x.decode() for x in data[0].split()]
        return []

    def get_msg(self, uid: str, timestamp: int = 0) -> dict[str, str]:
        """read email message by uid, may filter by timestamp"""
        result: dict[str, str] = {}

        if not self._conn:
            return result

        _, data = self._conn.fetch(uid, "(RFC822)")
        if not _ == "OK" or data is None or data[0] is None:
            return result

        item = data[0][1]
        if self.is_bytes(item):
            msg = message_from_bytes(bytes(item))
        else:
            msg = message_from_string(str(item))

        e_date = msg["Date"]
        time_stamp = parsedate_to_datetime(e_date).timestamp()
        if time_stamp and timestamp and time_stamp < timestamp:
            return result

        _, e_from = parseaddr(msg["From"])
        _, e_to = parseaddr(msg["To"])
        e_sub = decode_header(msg["Subject"])[0][0].decode(
            encoding=self.encoding, errors="ignore"
        )

        self.log(f"Raw date: {e_date}")
        self.log(f"Subject: {e_sub}")
        self.log(f"From: {e_from}")
        self.log(f"To: {e_to}")

        while msg.is_multipart():
            msg = msg.get_payload(0)
        body = msg.get_payload(decode=True)

        charset = self.guess_charset(msg)
        if charset:
            e_body = body.decode(charset)
        else:
            e_body = body.decode()

        e_date = self._to_str(msg["Date"])
        e_sub = self._to_str(e_sub)
        e_from = self._to_str(e_from)
        e_to = self._to_str(e_to)

        return {
            "uid": uid,
            "date": e_date,
            "subject": e_sub,
            "from": e_from,
            "to": e_to,
            "body": e_body,
        }

    def lookup(
        self,
        query: str,
        pattern: Pattern,
        timestamp: int = 0,
        debug: bool = False,
    ) -> list[str]:
        """lookup through mailbox and filter email content by regex"""
        result: list[str] = []
        for folder in self._folders:
            uids = self.get_uids(folder, query)
            for index, uid in enumerate(reversed(uids)):
                self.log(f"<index={index}> - <uid={uid}>")
                msg_data = self.get_msg(uid, timestamp)
                if not msg_data:
                    continue
                if debug:
                    print(f"index={index} - uid={uid}")
                    print(msg_data)
                    if self._debugger:
                        self._debugger.save(msg_data)
                found = pattern.findall(msg_data["body"])
                if found:
                    result.extend(found)

        return list(set(result))

    @staticmethod
    def _date_str(time_stamp: int = 0, days: int = 1) -> str:
        """generate date str"""
        fmt = "D-MMM-YYYY"
        if time_stamp:
            return arrow.get(time_stamp).format(fmt)
        return arrow.now().shift(days=-days).format(fmt)

    def search(
        self,
        from_email: str,
        to_email: str,
        subject: str,
        pattern: re.Pattern,
        time_stamp: int = 0,
        retry: int = 6,
        debug: bool = False,
    ) -> list[str]:
        """search email by various filters"""
        date_str = self._date_str(time_stamp=time_stamp)
        query = f'(SINCE {date_str} FROM "{from_email}" TO "{to_email}" SUBJECT "{subject}")'
        query = f'SUBJECT "{subject}"'
        for _ in range(retry):
            if self.login():
                results = self.lookup(query, pattern, time_stamp, debug)
                if results:
                    return results
            if debug:
                break
            time.sleep(60)
        return []

