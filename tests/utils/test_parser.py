
import regex as re

from pylib.utils.parser import BaseParser, HTMLParser


class Tester:
    """TestCase for BaseParser."""

    parser = BaseParser()
    document = """<html><head><title>Title</title></head> <body> <div id='div_one'> <ul> <li> list_item_0 </li> <br> <li> list_item_1 </li> </ul> </div> <br> <div id='div_two'> div_two_text </div>  <div id='div_two'> hello Hello</div>  </body></html>"""

    def test_to_node(self) -> None:
        """Return node and string for self.document."""
        doc_str = self.parser.as_str(document=self.document)
        doc_node = self.parser.as_node(document=self.document)
        assert isinstance(doc_str, str)
        assert isinstance(doc_node, HTMLParser)

    def test_remove_child(self) -> None:
        """Test remove child."""
        doc_node = self.parser.as_node(document=self.document)
        node = self.parser.remove_child(node=doc_node, selector="#div_one")
        assert "div_one" not in node.text()

    def test_collect_list(self) -> None:
        """Test collect list."""
        doc_node = self.parser.as_node(document=self.document)
        node, list_text = self.parser.collect_list(node=doc_node, selector="li")
        assert all("list_item" in text for text in list_text)
        assert "list_item" not in self.parser.as_str(node)

        doc_node = self.parser.as_node(document=self.document)
        node, list_text = self.parser.collect_list(
            node=doc_node, selector="li", remove=False
        )
        assert "list_item" in self.parser.as_str(node)

    def test_crlf(self) -> None:
        """Test crlf."""
        doc_node = self.parser.as_node(document=self.document)
        assert "<br>" in self.document
        node = self.parser.crlf(node=doc_node)
        assert "<br>" not in node.text()

    def test_attr(self) -> None:
        """Test attr."""
        doc_node = self.parser.as_node(document=self.document)
        node_div = doc_node.css_first("#div_one")
        assert self.parser.attr(node=node_div, name="id") == "div_one"

        doc_node = self.parser.as_node(document=self.document)
        attr_value = self.parser.first_attr(
            node=doc_node, selector="div", attr_name="id"
        )
        assert attr_value == "div_one"

        doc_node = self.parser.as_node(document=self.document)
        node, attr_value = self.parser.first_attr_opt(
            node=doc_node, selector="div", attr_name="id"
        )
        assert attr_value == "div_one"
        assert "div_one" in self.parser.as_str(node)

        doc_node = self.parser.as_node(document=self.document)
        node, attr_value = self.parser.first_attr_opt(
            node=doc_node, selector="div", attr_name="id", remove=True
        )
        assert attr_value == "div_one"
        assert "div_one" not in self.parser.as_str(node)

    def test_text(self) -> None:
        """Test text."""
        doc_node = self.parser.as_node(document=self.document)
        text = self.parser.first_text(node=doc_node, selector="#div_two")
        assert "div_two_text" in text
        assert len(text) > len("div_two_text")

        doc_node = self.parser.as_node(document=self.document)
        text = self.parser.first_text(node=doc_node, selector="#div_two", strip=True)
        assert "div_two_text" in text
        assert len(text) == len("div_two_text")

        doc_node = self.parser.as_node(document=self.document)
        node, text = self.parser.first_text_opt(node=doc_node, selector="#div_two")
        assert "div_two_text" in text
        assert "div_two_text" in self.parser.as_str(node)

        doc_node = self.parser.as_node(document=self.document)
        node, text = self.parser.first_text_opt(
            node=doc_node, selector="#div_two", remove=True
        )
        assert "div_two_text" in text
        assert "div_two_text" not in self.parser.as_str(node)

    def test_regex_find(self) -> None:
        """Test regex find."""
        found_str = self.parser.regex_find(text=self.document, raw=r"hello")
        assert found_str == "hello"
        found_str = self.parser.regex_find(
            text=self.document, raw=r"hello", flags=re.I, index=1
        )
        assert found_str == "Hello"

  