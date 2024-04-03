from typing import List, Tuple
from trading_framework.execution_client import ExecutionClient
from trading_framework.price_listener import PriceListener

class LimitOrderAgent(PriceListener):
    def __init__(self, execution_client: ExecutionClient) -> None:
        super().__init__()
        self.execution_client = execution_client
        self.orders: List[Tuple[bool, str, int, float]] = []  

    def add_order(self, buy: bool, product_id: str, amount: int, limit: float) -> None:
        self.orders.append((buy, product_id, amount, limit))

    def execute_orders(self, current_price: float) -> None:
        executed_orders = []
        for order in self.orders:
            buy, product_id, amount, limit = order
            if (buy and current_price <= limit) or (not buy and current_price >= limit):
                try:
                    if buy:
                        self.execution_client.buy(product_id, amount)
                    else:
                        self.execution_client.sell(product_id, amount)
                    executed_orders.append(order)
                except Exception as e:
                    print(f"Failed to execute order: {e}")
        # Remove executed orders from the list
        for order in executed_orders:
            self.orders.remove(order)

    def on_price_tick(self, product_id: str, price: float) -> None:
        self.execute_orders(price)

