from Exchange import Interface
import pytest

@pytest.fixture
def orders_package(monkeypatch):
    app = Interface()

    commands = [
        'BUY OPENAI LMT $100 5',
        'BUY OPENAI MKT 3',
        'SELL OPENAI MKT 3',
        'SELL OPENAI LMT $95 3',
        'SELL OPENAI LMT $98 7',
        'BUY OPENAI MKT 5',
        'SELL OPENAI MKT 10',
        'BUY GOOGLE LMT $300 10',
    ]

    for cmd in commands:
        monkeypatch.setattr('builtins.input', lambda _: cmd)
        app.parser()
    return app


def test_limit_order_creation(orders_package):
    #app = Interface()
    #monkeypatch.setattr('builtins.input', lambda _: 'BUY OPENAI LMT $100 5')
    #app.parser()
    app = orders_package
    assert len(app.order_book.orders) == 6
    order = app.order_book.orders[0]
    assert order.action == 'BUY'
    assert order.company == 'OPENAI'
    assert order.quantity == 5
    assert order.price == 100
    print('Книга ордеров', app.order_book.orders)


def find_order(orders, *, action, company, order_type, quantity):
    return next(
        (
            o for o in orders
            if o.action == action
            and o.company == company
            and o.order_type == order_type
            and o.quantity == quantity
        ),
        None,
    )


def test_mkt_order_creation(orders_package):
    app = orders_package
    order = find_order(
        app.order_book.orders,
        action='BUY',
        company='OPENAI',
        order_type='MKT',
        quantity=5,
    )

    assert order is not None
    assert order.price == 98
    assert order.status == 'FILLED'


def test_through_all(monkeypatch, capsys):
    inputs = iter(['', 'BUY SNAP LMT 150 10', 'VIEW ORDERS', 'QUIT'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    app = Interface()

    with pytest.raises(SystemExit):
        app.choose_interface()

    out = capsys.readouterr().out
    assert 'SNAP LMT BUY $150.0 0/10 PENDING' in out
    assert len(app.order_book.orders) == 1








