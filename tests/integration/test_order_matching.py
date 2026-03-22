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






