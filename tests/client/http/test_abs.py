USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


class AbsTester:
    """Abstract cls for HTTP Tester."""

    user_agent = USER_AGENTS[0]
    proxy_http = r"http://bpusr023:bppwd023@162.212.175.154:12345"
    proxy_socks = "socks5://127.0.0.1:9951"

    # test url for mock 429 errors, etc.
    url_mock = "https://example.com"

    # test url by httpbin.org
    url_headers = "https://httpbin.org/headers"
    url_ip = "https://httpbin.org/ip"

    url_delete = "https://httpbin.org/delete"
    url_get = "https://httpbin.org/get"
    url_patch = "https://httpbin.org/patch"
    url_post = "https://httpbin.org/post"
    url_put = "https://httpbin.org/put"


    # test url for download files
    # sometimes error, maybe due to website limiting..
    url_direct = r"https://raw.githubusercontent.com/br8km/DevPub/main/test_files/ai_beauty.jpg"

    url_ranges = r"https://raw.githubusercontent.com/br8km/DevPub/main/test_files/ai_beauty.zip"

    url_zip = r"https://raw.githubusercontent.com/br8km/DevPub/main/test_files/ai_beauty.zip"

    # Alternative Source: - "https://testfiledownload.com/"
    # Example: "http://ipv4.download.thinkbroadband.com/10MB.zip"