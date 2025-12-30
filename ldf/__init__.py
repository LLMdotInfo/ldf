"""LDF - LLM Development Framework.

A spec-driven development framework for AI-assisted software engineering.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("llm-ldf")
except PackageNotFoundError:
    # Package not installed (running from source without pip install -e .)
    __version__ = "0.0.0.dev"
