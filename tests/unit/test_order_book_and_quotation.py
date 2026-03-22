import pytest

from Exchange import Order, Quotation


def test_order_fill_full_sets_filled_status():
    order = Order('BUY', 'OPENAI', 'LMT', 100, 3)

    order.fill(3)

    assert order.filled_quantity == 3
    assert order.status == 'FILLED'
    assert order.remaining() == 0


def test_get_best_prices_filters_company_and_status(order_book):
    buy_openai = order_book.create_limit_order('BUY', 'OPENAI', 'LMT', 101, 4)
    buy_openai.fill(4)
    buy_google = order_book.create_limit_order('BUY', 'GOOGLE', 'LMT', 150, 5)
    sell_openai = order_book.create_limit_order('SELL', 'OPENAI', 'LMT', 99, 2)

    order_book.add_order(buy_openai)
    order_book.add_order(buy_google)
    order_book.add_order(sell_openai)

    best_bid, best_ask = order_book.get_best_prices('OPENAI')

    assert best_bid is None
    assert best_ask == 99


def test_add_limit_order_updates_storage_lists(order_book):
    buy = order_book.create_limit_order('BUY', 'OPENAI', 'LMT', 100, 2)
    sell = order_book.create_limit_order('SELL', 'OPENAI', 'LMT', 101, 2)

    order_book.add_order(buy)
    order_book.add_order(sell)

    assert buy in order_book.orders
    assert sell in order_book.orders
    assert buy in order_book.buy_lmt_orders
    assert sell in order_book.sell_lmt_orders


def test_add_market_buy_uses_best_ask_and_records_trade(order_book):
    ask = order_book.create_limit_order('SELL', 'OPENAI', 'LMT', 104, 8)
    market_buy = order_book.create_market_order('BUY', 'OPENAI', 'MKT', 3)
    order_book.add_order(ask)

    order_book.add_order(market_buy)

    assert market_buy.price == 104
    assert market_buy.status == 'FILLED'
    assert market_buy.filled_quantity == 3
    assert order_book.last_trade_price['OPENAI'] == 104


def test_add_market_sell_uses_best_bid_and_records_trade(order_book):
    bid = order_book.create_limit_order('BUY', 'OPENAI', 'LMT', 103, 8)
    market_sell = order_book.create_market_order('SELL', 'OPENAI', 'MKT', 3)
    order_book.add_order(bid)

    order_book.add_order(market_sell)

    assert market_sell.price == 103
    assert market_sell.status == 'FILLED'
    assert market_sell.filled_quantity == 3
    assert order_book.last_trade_price['OPENAI'] == 103


@pytest.mark.parametrize(
    ('action', 'expected_message_part'),
    [
        ('BUY', 'buy'),
        ('SELL', 'sell'),
    ],
)
def test_add_market_without_liquidity_raises_and_cancels(
    order_book, action, expected_message_part
):
    market_order = order_book.create_market_order(action, 'OPENAI', 'MKT', 1)

    with pytest.raises(ValueError) as exc_info:
        order_book.add_order(market_order)

    assert market_order.status == 'CANCELLED'
    assert expected_message_part in str(exc_info.value).lower()


def test_create_market_order_has_none_price(order_book):
    order = order_book.create_market_order('BUY', 'OPENAI', 'MKT', 7)

    assert order.price is None
    assert order.quantity == 7
    assert order.order_type == 'MKT'


def test_quotation_prints_best_prices_and_last_trade(order_book, capsys):
    order_book.add_order(
        order_book.create_limit_order('BUY', 'OPENAI', 'LMT', 101, 2)
    )
    order_book.add_order(
        order_book.create_limit_order('SELL', 'OPENAI', 'LMT', 103, 2)
    )
    order_book.record_trade('OPENAI', 102)

    Quotation.print_last_price(order_book, 'OPENAI')

    out = capsys.readouterr().out
    assert 'OPENAI BID: 101 ASK: 103, LAST: 102' in out


def test_quotation_prints_no_orders_message_when_book_empty(
    order_book, capsys
):
    Quotation.print_last_price(order_book, 'OPENAI')

    out = capsys.readouterr().out
    assert 'OPENAI' in out
