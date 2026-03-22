import pytest
from Exchange import Order, OrderBook


def test_order_partial():
    order = Order('BUY', 'OPENAI', 'LMT', 100, 10)
    order.fill(4)
    assert order.filled_quantity == 4
    assert order.status == 'PARTIAL'
    assert order.remaining() == 6


def test_validate_price_raises_for_zero():
    with pytest.raises(ValueError):
        OrderBook.validate_price(0)
