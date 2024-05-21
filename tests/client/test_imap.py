import arrow
import pytest
import regex as re

from pylib.client.imap import ImapClient
from pylib.utils.debugger import Debugger
from ..conftest import DIR_TEMP


class Tester:
    """Tester."""

    client: ImapClient

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_imap(self) -> None:
        """Run Test.

        show case for search substack password reset url
        Note: ts <= 365 days

        """

        client = ImapClient(
            host="",
            port=0,
            usr="",
            pwd="",
            ssl_enable=True,
            demo=True,
            proxy=None,
            debugger=Debugger(
                name="tester.ImapClient",
                dir=DIR_TEMP,
            ),
        )

        #  from_email = "no-reply@substack.com"
        #  to_email = "steemit2@vnomail.com"
        #  subject = "Set your password for Substack"
        #  pattern = r'(http:\/\/email\.mg1\.substack\.com\/c\/[\S]+?)"'

        from_email = "skylif@outlook.com"
        to_email = "pdfx@vnomail.com"
        subject = "just another testing"
        pattern = r"someone else"
        pattern = re.compile(pattern, re.I)
        time_stamp = int(arrow.now().shift(days=-365).timestamp())
        result = client.search(
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            pattern=pattern,
            time_stamp=time_stamp,
            retry=6,
            debug=True,
        )
        assert result
