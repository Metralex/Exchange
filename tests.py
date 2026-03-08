from Exchange import Order, StockExchangeQuotation
import pytest

def test_order_creation():
    order = Order("BUY", "SNAP", "LMT", 30, 100)
    assert order.status == "Pending"
    assert order.remaining() == 100

def test_partial_fill():
    order = Order("BUY", "SNAP", "LMT", 30, 100)
    order.fill(50)
    assert order.status == "Partial"
    assert order.remaining() == 50

# Интеграционные тесты
def test_order_matching():
    exchange = StockExchangeQuotation()
    buy_order = exchange.create_limit_order("BUY", "SNAP", "LMT", 30, 100)
    sell_order = exchange.create_market_order("SELL", "SNAP", "LMT", 30)
    exchange.match_orders()
    assert buy_order.status == "Filled"
    assert sell_order.status == "Filled"

# Тесты крайних случаев
def test_invalid_quantity():
    with pytest.raises(ValueError):
        Order("BUY", "SNAP", "LMT", 30, -10)

def test_zero_price():
    with pytest.raises(ValueError):
        Order("BUY", "SNAP", "LMT", 0, 100)
