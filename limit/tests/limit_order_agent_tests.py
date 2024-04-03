import unittest
from unittest.mock import Mock
from limit.limit_order_agent import LimitOrderAgent
from trading_framework.execution_client import ExecutionException

class TestLimitOrderAgent(unittest.TestCase):
    def test_add_order(self):
        execution_client = Mock()
        agent = LimitOrderAgent(execution_client)
        agent.add_order(buy=True, product_id="IBM", amount=1000, limit=100)
        self.assertEqual(len(agent.orders), 1)
        self.assertEqual(agent.orders[0], (True, "IBM", 1000, 100))

    def test_execute_orders(self):
        execution_client = Mock()
        agent = LimitOrderAgent(execution_client)
        agent.add_order(buy=True, product_id="IBM", amount=1000, limit=100)
        agent.add_order(buy=False, product_id="GOOG", amount=500, limit=200)
        agent.execute_orders(99)  
        execution_client.buy.assert_called_once_with("IBM", 1000)
        execution_client.reset_mock()
        agent.execute_orders(150)  
        execution_client.buy.assert_not_called()
        agent.execute_orders(199) 
        execution_client.sell.assert_called_once_with("GOOG", 500)

    def test_on_price_tick(self):
        execution_client = Mock()
        agent = LimitOrderAgent(execution_client)
        agent.add_order(buy=True, product_id="IBM", amount=1000, limit=100)
        agent.add_order(buy=False, product_id="GOOG", amount=500, limit=200)
        agent.on_price_tick("IBM", 99)  
        execution_client.buy.assert_called_once_with("IBM", 1000)
        execution_client.reset_mock()
        agent.on_price_tick("IBM", 150)  
        execution_client.buy.assert_not_called()
        agent.on_price_tick("GOOG", 199)  
        execution_client.sell.assert_called_once_with("GOOG", 500)

    def test_execute_orders_exception(self):
        execution_client = Mock()
        execution_client.buy.side_effect = ExecutionException("Error buying")
        agent = LimitOrderAgent(execution_client)
        agent.add_order(buy=True, product_id="IBM", amount=1000, limit=100)
        agent.execute_orders(99)
        execution_client.buy.assert_called_once_with("IBM", 1000)
        self.assertEqual(len(agent.orders), 1)  
