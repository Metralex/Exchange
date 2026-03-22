from Exchange import Interface


def test_parser_create_limit_order(monkeypatch):
    app = Interface()
    monkeypatch.setattr('builtins.input', lambda _: 'BUY OPENAI LMT $100 5')

    app.parser()

    assert len(app.order_book.orders) == 1
    order = app.order_book.orders[0]
    assert order.action == 'BUY'
    assert order.company == 'OPENAI'
    assert order.quantity == 5
    assert order.price == 100


def test_parser_quote_calls_quotation(monkeypatch):
    app = Interface()
    called = {'value': False}

    def fake_print_last_price(order_book, company):
        called['value'] = True
        assert company == 'OPENAI'

    monkeypatch.setattr('builtins.input', lambda _: 'QUOTE OPENAI')
    monkeypatch.setattr(
        app.quotation, 'print_last_price', fake_print_last_price
    )

    app.parser()

    assert called['value'] is True


def test_parser_switch_interface_changes_mode(monkeypatch):
    app = Interface()
    assert app.current_mode == 'terminal'
    monkeypatch.setattr('builtins.input', lambda _: 'SWITCH INTERFACE')

    app.parser()

    assert app.current_mode == 'menu'


def test_parser_invalid_company_does_not_add_order(monkeypatch):
    app = Interface()
    monkeypatch.setattr('builtins.input', lambda _: 'BUY UNKNOWN LMT $100 5')

    app.parser()

    assert len(app.order_book.orders) == 0
