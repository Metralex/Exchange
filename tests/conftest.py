import pytest

from Exchange import Interface, MatchingEngine, OrderBook


@pytest.fixture
def order_book():
    return OrderBook()


@pytest.fixture
def matching_engine():
    return MatchingEngine()


@pytest.fixture
def interface_app():
    return Interface()
