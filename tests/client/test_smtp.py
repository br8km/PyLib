import pytest

from pylib.client.smtp import SMTPClient


class Tester:
    """Tester."""

    client: SMTPClient

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_smtp(self) -> None:
        """Run Test.

        show case for search substack password reset url
        Note: ts <= 365 days

        """


        client = SMTPClient(
            host="",
            port=0,
            usr="",
            pwd="",
            use_ssl=True,
        )

        assert client

