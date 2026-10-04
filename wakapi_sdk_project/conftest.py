"""Shared pytest configuration for the vendored SDK test suite."""

import os


def pytest_configure(config):
    """Keep tests off ambient HTTP proxies.

    httpx honours ``ALL_PROXY``/``HTTPS_PROXY`` from the environment, and a SOCKS
    proxy needs the optional ``socksio`` dependency that the project does not
    ship. Tests must reach the server under test directly.
    """
    for var in (
        "ALL_PROXY",
        "all_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "HTTPS_PROXY",
        "https_proxy",
    ):
        os.environ.pop(var, None)
