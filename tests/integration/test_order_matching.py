from Exchange import OrderBook, MatchingEngine


def test_limit_orders_matching():
    book = OrderBook()
    engine = MatchingEngine()

    buy = book.create_limit_order('BUY', 'OPENAI', 'LMT', 105, 10)
    sell = book.create_limit_order('SELL', 'OPENAI', 'LMT', 100, 6)

    book.add_order(buy)
    book.add_order(sell)
    engine.match_orders(book)

    assert buy.status == 'PARTIAL'
    assert buy.filled_quantity == 6
    assert sell.status == 'FILLED'
    assert book.last_trade_price['OPENAI'] == 100


def test_match_orders_does_not_match_if_prices_do_not_cross():
    book = OrderBook()
    engine = MatchingEngine()

    buy = book.create_limit_order('BUY', 'OPENAI', 'LMT', 100, 5)
    sell = book.create_limit_order('SELL', 'OPENAI', 'LMT', 101, 5)

    book.add_order(buy)
    book.add_order(sell)
    engine.match_orders(book)

    assert buy.status == 'PENDING'
    assert sell.status == 'PENDING'
    assert 'OPENAI' not in book.last_trade_price


def test_match_orders_uses_price_time_priority_for_same_company():
    book = OrderBook()
    engine = MatchingEngine()

    buy_low = book.create_limit_order('BUY', 'OPENAI', 'LMT', 100, 4)
    buy_high = book.create_limit_order('BUY', 'OPENAI', 'LMT', 105, 4)
    sell = book.create_limit_order('SELL', 'OPENAI', 'LMT', 100, 3)

    book.add_order(buy_low)
    book.add_order(buy_high)
    book.add_order(sell)
    engine.match_orders(book)

    assert buy_high.filled_quantity == 3
    assert buy_high.status == 'PARTIAL'
    assert buy_low.filled_quantity == 0
    assert buy_low.status == 'PENDING'
    assert sell.status == 'FILLED'
