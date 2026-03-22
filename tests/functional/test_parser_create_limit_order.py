from Exchange import Interface

def test_parser_create_limit_order(monkeypatch):
    app = Interface()
    monkeypatch.setattr('builtins.input', lambda _: 'BUY OPENAI LMT $100 5')

    app.parser()

    assert len(app.order_book.orders) == 1
    order = app.order_book.orders[0]
    assert order.action == 'BUY'
    assert order.company == 'OPENAI'
    assert order.price == 100
    assert order.filled_quantity == 5