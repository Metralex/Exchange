from datetime import datetime
from enum import Enum


class UserAction(Enum):
    PLACE_BUY_MKT = 1
    PLACE_SELL_MKT = 2
    PLACE_BUY_LMT = 3
    PLACE_SELL_LMT = 4
    GET_QUOTE = 5
    VIEW_ORDERS = 6
    SWITCH_MODE = 7
    EXIT = 8

    def description(self):
        descriptions = {
            UserAction.PLACE_BUY_MKT: 'Разместить рыночный ордер на покупку',
            UserAction.PLACE_SELL_MKT: 'Разместить рыночный ордер на продажу',
            UserAction.PLACE_BUY_LMT: 'Разместить лимитный ордер на покупку',
            UserAction.PLACE_SELL_LMT: 'Разместить лимитный ордер на продажу',
            UserAction.GET_QUOTE: 'Получить последнюю цену ордера',
            UserAction.VIEW_ORDERS: 'Просмотреть ордера',
            UserAction.SWITCH_MODE: 'Переключиться в терминал',
            UserAction.EXIT: 'Выход',
        }
        return descriptions.get(self, 'Неизвестное действие')


class Interface:
    def __init__(self):
        self.menu = False
        self.number = None
        self.order_book = OrderBook()
        self.quotation = Quotation()
        self.matching = MatchingEngine()
        self.companies = self.order_book.companies
        self.current_mode = 'terminal'

    def parser(self):
        try:
            print('Введите команду')
            order_command = input('Action: ').upper().strip()

            if order_command == 'VIEW ORDERS':
                self.order_book.view_orders()
                return

            if order_command == 'SWITCH INTERFACE':
                self.current_mode = 'menu'
                print('Переключено в режим меню')
                return

            if order_command == 'QUIT':
                exit()

            order_list = order_command.split()
            # print(order_list)

            if not order_list:
                raise ValueError('Пустая строка')

            if order_list[0] == 'QUOTE':
                if len(order_list) < 2:
                    raise IndexError('Введите название компании')
                if order_list[1] in self.companies:
                    self.quotation.get_last_price(
                        self.order_book, order_list[1]
                    )
                else:
                    raise ValueError('Компании нет на бирже')
                return

            if len(order_list) < 4:
                raise ValueError('В команде не хватает параметров')

            action = order_list[0]
            company = order_list[1]
            order_type = order_list[2]

            if action not in ['BUY', 'SELL']:
                raise ValueError('Неизвестная команда')

            if company not in self.companies:
                raise ValueError('Выбранной компании нет на бирже')

            if order_type == 'LMT':
                if len(order_list) < 5:
                    raise ValueError('Для LMT нужны price и quantity')
                price = float(order_list[3].replace('$', ''))
                quantity = int(order_list[4])
                if price <= 0:
                    raise ValueError('Стоимость должна быть больше нуля')
                if quantity <= 0:
                    raise ValueError('Количество должно быть больше нуля')
                new_order = self.order_book.create_limit_order(
                    action, company, order_type, price, quantity
                )
            elif order_type == 'MKT':
                quantity = int(order_list[3])
                if quantity <= 0:
                    raise ValueError('Количество должно быть больше нуля')
                new_order = self.order_book.create_market_order(
                    action, company, order_type, quantity
                )
            else:
                raise ValueError('Неверный тип ордера')
            self.order_book.add_order(new_order)
            if new_order.order_type == 'LMT':
                self.matching.match_orders(self.order_book)
            self.quotation.update_prices(self.order_book)

        except ValueError as ve:
            print(f'Ошибка валидации: {ve}')
            return

        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            print('Попробуйте другую команду')
            return

    def choose_interface(self):

        print('Выберите способ ввода:')
        print(
            '1. Терминал (по умолчанию)\n'
            '2. Меню выбора\n'
            'Чтобы пропустить нажмите Enter'
        )

        number = input('Action: ')
        if number == '2':
            self.current_mode = 'menu'

        while True:
            if self.current_mode == 'menu':
                self.run_menu()
            elif self.current_mode == 'terminal':
                self.parser()

    def action_definer(self):

        print('\nВыберите действие и введите его номер:')
        for action in UserAction:
            print(f'{action.value}. {action.description()}')

        try:
            choice = int(input('Action: '))
            selected_action = UserAction(choice)
            if selected_action is None:
                raise ValueError(f'Нет действия с номером {choice}')
            return selected_action
        except (ValueError, KeyError):
            print('Неверный ввод. Попробуйте снова.')
            return self.action_definer()

    def run_menu(self):
        try:
            action = self.action_definer()

            if action == UserAction.GET_QUOTE:
                print(*enumerate(self.companies), sep='\n')
                print('Введите номер компании:')
                company_index = int(input('Company: '))
                if company_index not in range(len(self.companies)):
                    raise ValueError('Такого номера нет в списке')
                else:
                    self.quotation.get_last_price(
                        self.order_book, self.companies[company_index]
                    )

            elif action == UserAction.VIEW_ORDERS:
                self.order_book.view_orders()

            elif action == UserAction.SWITCH_MODE:
                self.current_mode = 'terminal'
                print('Переключено в терминал')

            elif action == UserAction.EXIT:
                print('Выход из программы')
                exit()

            if (
                action == UserAction.PLACE_BUY_MKT
                or action == UserAction.PLACE_SELL_MKT
                or action == UserAction.PLACE_BUY_LMT
                or action == UserAction.PLACE_SELL_LMT
            ):
                print('Введите номер выбранной компании:')
                print(*enumerate(self.companies), sep='\n')
                company_index = int(input('Action: '))
                if company_index not in range(len(self.companies)):
                    raise ValueError('Такого номера нет в списке')
                company = self.companies[company_index]
                print('Введите количество')
                quantity = int(input('Action: '))
                if quantity <= 0:
                    raise ValueError('Количество должно быть больше нуля')

            if (
                action == UserAction.PLACE_BUY_MKT
                or action == UserAction.PLACE_SELL_MKT
            ):
                if action == UserAction.PLACE_BUY_MKT:
                    new_order = self.order_book.create_market_order(
                        'BUY', company, 'MKT', quantity
                    )
                elif action == UserAction.PLACE_SELL_MKT:
                    new_order = self.order_book.create_market_order(
                        'SELL', company, 'MKT', quantity
                    )
                self.order_book.add_order(new_order)
                self.quotation.update_prices(self.order_book)

            elif (
                action == UserAction.PLACE_BUY_LMT
                or action == UserAction.PLACE_SELL_LMT
            ):
                print('Введите цену за одну единицу в $:')
                price = float(input('Action: '))
                if price <= 0:
                    raise ValueError('Стоимость должна быть больше нуля')
                if action == UserAction.PLACE_BUY_LMT:
                    new_order = self.order_book.create_limit_order(
                        'BUY', company, 'LMT', price, quantity
                    )
                elif action == UserAction.PLACE_SELL_LMT:
                    new_order = self.order_book.create_limit_order(
                        'SELL', company, 'LMT', price, quantity
                    )
                self.order_book.add_order(new_order)
                if new_order.order_type == 'LMT':
                    self.matching.match_orders(self.order_book)
                self.quotation.update_prices(self.order_book)

        except ValueError:
            print('Необходимо ввести число от 1 до 8')


class Order:
    def __init__(self, action, company, order_type, price, quantity):
        self.action = action
        self.company = company
        self.order_type = order_type
        self.stock = None
        self.price = price
        self.quantity = quantity
        self.status = 'PENDING'
        self.filled_quantity = 0
        self.timestamp = datetime.now()

    def fill(self, amount):
        self.filled_quantity += amount
        if self.filled_quantity == self.quantity:
            self.status = 'FILLED'
        elif self.filled_quantity > 0:
            self.status = 'PARTIAL'

    def remaining(self):
        return self.quantity - self.filled_quantity


class OrderBook:
    def __init__(self):
        self.companies = [
            'SNAP',
            'GOOGLE',
            'AMAZON',
            'OPENAI',
            'FB',
            'YANDEX',
            'NVIDIA',
        ]
        self.sell_lmt_orders = []
        self.buy_lmt_orders = []
        self.orders = []
        self.bid = 0
        self.ask = 0

    @staticmethod
    def create_limit_order(action, company, order_type, price, quantity):
        OrderBook.validate_price(price)
        new_order = Order(action, company, order_type, price, quantity)
        return new_order

    @staticmethod
    def create_market_order(action, company, order_type, quantity):
        new_order = Order(action, company, order_type, None, quantity)
        return new_order

    @staticmethod
    def validate_price(price):
        if price <= 0:
            raise ValueError('Цена должна быть положительной')

    def view_orders(self):
        if self.orders:
            for order in self.orders:
                print(
                    f'{order.company} {order.order_type} {order.action}'
                    f' ${order.price} {order.filled_quantity}/{order.quantity} {order.status}'
                )
        else:
            print('Ордеров нет')

    def add_order(self, order):
        self.orders.append(order)
        if order.order_type == 'LMT':
            if order.action == 'BUY':
                self.buy_lmt_orders.append(order)
            if order.action == 'SELL':
                self.sell_lmt_orders.append(order)
        if order.order_type == 'LMT':
            print(
                f'You have placed a limit'
                f' {order.action.lower()} order for {order.quantity} {order.company} '
                f'shares at ${order.price} each'
            )
        elif order.order_type == 'MKT':
            company_buy_prices = [
                order.price
                for order in self.buy_lmt_orders
                if order.company == order.company
                and order.status in ('PENDING', 'PARTIAL')
            ]
            company_sell_prices = [
                o.price
                for o in self.sell_lmt_orders
                if o.company == order.company
                and o.status in ('PENDING', 'PARTIAL')
            ]
            best_bid = max(company_buy_prices, default=0)
            best_ask = min(company_sell_prices, default=0)
            if order.action == 'BUY':
                order.price = best_ask
            if order.action == 'SELL':
                order.price = best_bid
            order.filled_quantity = order.quantity
            order.status = 'FILLED'
            print(
                f'You have placed a market order for {order.quantity} {order.company} '
                f'shares.'
            )


class Quotation:
    def update_prices(self, order_book):
        if order_book.buy_lmt_orders:
            order_book.bid = max(
                order.price for order in order_book.buy_lmt_orders
            )
        else:
            order_book.bid = 0

        if order_book.sell_lmt_orders:
            order_book.ask = min(
                order.price for order in order_book.sell_lmt_orders
            )
        else:
            order_book.ask = 0

    def get_last_price(self, order_book, company):
        company_buy = [
            order
            for order in order_book.buy_lmt_orders
            if order.company == company
            and order.status in ('PENDING', 'PARTIAL')
        ]

        company_sell = [
            order
            for order in order_book.sell_lmt_orders
            if order.company == company
            and order.status in ('PENDING', 'PARTIAL')
        ]

        bid = max((order.price for order in company_buy), default=0)
        ask = min((order.price for order in company_sell), default=0)

        current_company_list = [
            order
            for order in order_book.orders
            if (
                order.company == company
                and order.filled_quantity > 0
                and order.price is not None
            )
        ]
        if current_company_list:
            print(
                f'{company} BID: {bid} ASK: {ask}, LAST: {current_company_list[-1].price}'
            )
        else:
            print(
                f'Ордера на покупку/продажу акций компании {company} не выставлялись'
            )


class MatchingEngine:
    def match_orders(self, order_book):
        order_book.buy_lmt_orders.sort(key=lambda x: (-x.price, x.timestamp))
        order_book.sell_lmt_orders.sort(key=lambda x: (x.price, x.timestamp))
        for buy_order in order_book.buy_lmt_orders:
            for sell_order in order_book.sell_lmt_orders:
                if (
                    buy_order.price >= sell_order.price
                    and buy_order.status in ('PENDING', 'PARTIAL')
                    and sell_order.status in ('PENDING', 'PARTIAL')
                    and buy_order.company == sell_order.company
                ):
                    buy_remaining = (
                        buy_order.quantity - buy_order.filled_quantity
                    )
                    sell_remaining = (
                        sell_order.quantity - sell_order.filled_quantity
                    )
                    fill_amount = min(buy_remaining, sell_remaining)
                    buy_order.fill(fill_amount)
                    sell_order.fill(fill_amount)


app = Interface()
app.choose_interface()
