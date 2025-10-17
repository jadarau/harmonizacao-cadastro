"""Test configuration and fixtures."""
import os
import sys
import pytest
import asyncio
from typing import AsyncGenerator

# Garantir que o diretório raiz esteja no PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_text_content():
    """Sample text content for testing."""
    return """
    Este é um documento de teste sobre harmonização fiscal.
    
    A harmonização fiscal é um processo importante para alinhar
    as políticas tributárias entre diferentes jurisdições.
    
    Os principais benefícios incluem:
    1. Redução da evasão fiscal
    2. Maior transparência
    3. Facilita o comércio internacional
    
    O processo envolve várias etapas de negociação e implementação.
    """


@pytest.fixture
def sample_document_metadata():
    """Sample document metadata for testing."""
    return {
        "author": "Test Author",
        "category": "fiscal",
        "language": "pt"
    }