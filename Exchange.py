from datetime import datetime

class Interface:
    def __init__(self):
        self.menu = False
        self.number = None
        self.companies = ['SNAP', 'GOOGLE', 'AMAZON', 'OPENAI', 'FB', 'YANDEX', 'NVIDIA']
        self.exchange = StockExchangeQuotation()
        self.current_mode = 'terminal'

    def parser(self):
        try:
            print('Введите команду')
            order_str = input('Action: ').upper()
            #order_command = order_str.replace('Action: ', '').strip()
            order_command = order_str.strip()

            if order_command == 'VIEW ORDERS':
                self.exchange.view_orders()
                return

            if order_command == 'SWITCH INTERFACE':
                self.current_mode = 'menu'
                print('Переключено в режим меню')
                return

            if order_command == 'QUIT':
                exit()

            order_list = order_command.split()
            #print(order_list)

            if not order_list:
                raise ValueError('Пустая строка')

            if order_list[0] == 'QUOTE':
                if order_list[1] in self.companies:
                    self.exchange.show_prices(order_list[1])
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
                price = float(order_list[3].replace('$', ''))
                quantity = int(order_list[4])
                if price < 0:
                    raise ValueError('Стоимость должна быть больше нуля')
                new_order = self.exchange.create_limit_order(action, company, order_type, price, quantity)
            elif order_type == 'MKT':
                quantity = int(order_list[3])
                new_order = self.exchange.create_market_order(action, company, order_type, quantity)
            else:
                raise ValueError('Неверный тип ордера')

            if quantity < 0:
                raise ValueError('Количество должно быть больше нуля')

            #print('валидация прошла успешно')

            self.exchange.add_order(new_order)

            #print('Операция выполнена')
            #exchange.view_orders()
            #return action, company, order_type, price, quantity

        except ValueError as ve:
            print(f'Ошибка валидации: {ve}')
            return

        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            print('Попробуйте другую команду')
            return

    def choose_interface(self):

        print('Выберите способ ввода:')
        print('1. Терминал (по умолчанию)\n'
              '2. Меню выбора\n'
              'Чтобы пропустить нажмите Enter')

        number =  input('Action: ')
        if number == '2':
            self.current_mode = 'menu'

        while True:
            if self.current_mode == 'menu':
                self.action_definer()
            elif self.current_mode == 'terminal':
                self.parser()



    def action_definer(self):

        #while True:
        print('Выберите действие и введите его номер:')
        print('1. Разместить рыночный ордер на покупку\n'
              '2. Разместить рыночный ордер на продажу\n'
              '3. Разместить лимитный ордер на покупку\n'
              '4. Разместить лимитный ордер на продажу\n'
              '5. Получить последнюю цену ордера\n'
              '6. Просмотреть ордера\n'
              '7. Переключиться в режим терминала\n'
              '8. Выход')

        self.number = input('Action: ')
        try:
            self.number = int(self.number)
            if self.number in range(1, 5):
                try:
                    while True:
                        action = 'BUY' if self.number == (1 and 3) else 'SELL'
                        order_type = 'LMT' if self.number == (2 and 4) else 'MKT'
                        print('Введите номер выбранной компании:')
                        print(*enumerate(self.companies), sep='\n')
                        company_index = int(input('Action: '))
                        company = self.companies[company_index]
                        print('Введите количество')
                        quantity = int(input('Action: '))
                        if order_type == 'LMT':
                            print('Введите цену за одну единицу в $:')
                            price = float(input('Action: '))
                            new_order = self.exchange.create_limit_order(action, company, order_type, price, quantity)
                        else:
                            new_order = self.exchange.create_market_order(action, company, order_type, quantity)
                        self.exchange.add_order(new_order)
                        break

                except ValueError:
                    print('Вводите только числа')

            if self.number == 5:
                print(*enumerate(self.companies), sep='\n')
                print('Введите номер компании:')
                company_index = int(input('Company: '))
                if company_index not in range(len(self.companies)):
                    raise ValueError('Такого номера нет в списке')
                else:
                    self.exchange.show_prices(self.companies[company_index])

            if self.number == 6:
                self.exchange.view_orders()

            if self.number == 7:
                self.current_mode = 'terminal'
                print('Переключено в терминал')

            if self.number == 8:
                print('Выход из программы')
                exit()



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


class StockExchangeQuotation:
    def __init__(self):
        self.sell_lmt_orders = []
        self.buy_lmt_orders = []
        self.orders = []
        self.bid = 0
        self.ask = 0
        self.filled = 0


    @staticmethod
    def create_limit_order(action, company, order_type, price, quantity):
        new_order = Order(action, company, order_type, price, quantity)
        return new_order

    @staticmethod
    def create_market_order(action, company, order_type, quantity):
        new_order = Order(action, company, order_type, None, quantity)
        return new_order

    def view_orders(self):
        if self.orders:
            for order in self.orders:
                print(f'{order.company} {order.order_type} {order.action}'
                      f' ${order.price} {order.filled_quantity}/{order.quantity} {order.status}')
        else:
            print('Ордеров нет')

    def add_order(self, order):
        self.orders.append(order)
        if order.order_type == 'LMT':
            if order.action == 'BUY':
                self.buy_lmt_orders.append(order)
            if order.action == 'SELL':
                self.sell_lmt_orders.append(order)
        self.update_prices()
        if order.order_type == 'LMT':
            self.match_orders()
            print(f'You have placed a limit'
                  f' {order.action.lower()} order for {order.quantity} {order.company} '
                  f'shares at ${order.price} each')
        elif order.order_type == 'MKT':
            if order.action == 'BUY':
                order.price = self.ask
            if order.action == 'SELL':
                order.price = self.bid
            order.filled_quantity = order.quantity
            order.status = f'{order.filled_quantity}/{order.quantity} FILLED'
            print(f'You have placed a market order for {order.quantity} {order.company} '
                  f'shares.')


    def update_prices(self):
        if self.buy_lmt_orders:
            self.bid = max(order.price for order in self.buy_lmt_orders)
        else:
            self.bid = 0

        if self.sell_lmt_orders:
            self.ask = min(order.price for order in self.sell_lmt_orders)
        else:
            self.ask = 0

    def show_prices(self, company):
        #print(f"Проверяем компанию: {repr(company)}")
        #print(f"Всего ордеров в системе: {len(self.orders)}")

        current_company_list = [order for order in self.orders if (order.company == company and
                                                                   order.filled_quantity > 0)]
        if current_company_list:
            print(f'{company} BID: {self.bid} ASK: {self.ask}, LAST: {current_company_list[-1].price}')
        else:
            print(f'Ордера на покупку/продажу акций компании {company} не выставлялись')

    def match_orders(self):
        self.buy_lmt_orders.sort(key=lambda x: (-x.price, x.timestamp))
        self.sell_lmt_orders.sort(key=lambda x: (x.price, x.timestamp))
        for buy_order in self.buy_lmt_orders:
            for sell_order in self.sell_lmt_orders:
                if (buy_order.price >= sell_order.price and
                    buy_order.status == 'PENDING' and
                    sell_order.status == 'PENDING' and
                    buy_order.company == sell_order.company):
                    buy_remaining = buy_order.quantity - buy_order.filled_quantity
                    sell_remaining = sell_order.quantity - sell_order.filled_quantity
                    fill_amount = min(buy_remaining, sell_remaining)
                    buy_order.fill(fill_amount)
                    sell_order.fill(fill_amount)



app = Interface()
app.choose_interface()




