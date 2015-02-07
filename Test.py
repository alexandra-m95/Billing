__author__ = 'alexandra'
import unittest
from Billing import Billing
from all_data import Data


class Test(unittest.TestCase):
    def setUp(self):
        self.data = Data()
        self.billing = Billing()
        self.data.set_current_log_file("Tests/test1")

    def test_add_valid_costs(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.result = {'http://192.168.65.101/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1': 35.0, 'http://callider/pause/index/tv/useUser': 13.0, 'http://callider/pause/index/pause/ajaxPause?pauseConfigId=&admin=0': 4.0}
        self.assertDictEqual(self.result, costs)

    def test_add_invalid_costs_1(self):
        self.data.set_current_costs_file("Tests/negative_number")
        costs = self.billing.add_costs_of_resources(self.data)
        self.result = {}
        self.assertDictEqual(self.result, costs)

    def test_add_invalid_costs_2(self):
        self.data.set_current_costs_file("Tests/non-numerical_param")
        costs = self.billing.add_costs_of_resources(self.data)
        self.result = {}
        self.assertDictEqual(self.result, costs)

    def test_add_invalid_costs_3(self):
        self.data.set_current_costs_file("Tests/invalid_url")
        costs = self.billing.add_costs_of_resources(self.data)
        self.result = {}
        self.assertDictEqual(self.result, costs)

    def test_number_bytes_for_resources(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        number_bytes_for_resources = data_for_resources[0]
        self.result = {('http://192.168.65.101/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.65.56': 9471}, ('http://192.168.65.101/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '17/Feb/2013'): {'192.168.65.56': 6343777}, ('http://callider.kontur/site/index/tv/useUser', '17/Feb/2013'): {'192.168.12.9': 43310}, ('http://callider/graph/personal/tv/useUser', '17/Feb/2013'): {'192.168.74.93': 86802, '192.168.12.67': 71545, '192.168.12.42': 58562}, ('http://192.168.65.101/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '18/Feb/2013'): {'192.168.65.56': 1567631}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=&admin=0', '18/Feb/2013'): {'192.168.12.61': 1753593}, ('http://callider.kontur/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.74.151': 2913330}, ('http://callider/pause/index/tv/useUser', '18/Feb/2013'): {'192.168.12.61': 13365}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=&admin=0', '17/Feb/2013'): {'192.168.12.61': 5185974}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '17/Feb/2013'): {'192.168.12.61': 13365}, ('http://callider/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.12.61': 13365}, ('http://callider/graph/personal/tv/useUser', '18/Feb/2013'): {'192.168.12.42': 58562}}
        self.assertDictEqual(self.result, number_bytes_for_resources)

    def test_number_visits_for_resources(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        number_visits_for_resources = data_for_resources[1]
        self.result = {('http://callider/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.12.61': 1}, ('http://callider.kontur/site/index/tv/useUser', '17/Feb/2013'): {'192.168.12.9': 1}, ('http://callider/pause/index/tv/useUser', '18/Feb/2013'): {'192.168.12.61': 1}, ('http://192.168.65.101/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '18/Feb/2013'): {'192.168.65.56': 3}, ('http://192.168.65.101/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.65.56': 1}, ('http://callider/graph/personal/tv/useUser', '17/Feb/2013'): {'192.168.74.93': 1, '192.168.12.42': 1, '192.168.12.67': 1}, ('http://callider/graph/personal/tv/useUser', '18/Feb/2013'): {'192.168.12.42': 1}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=&admin=0', '17/Feb/2013'): {'192.168.12.61': 6}, ('http://callider.kontur/pause/index/tv/useUser', '17/Feb/2013'): {'192.168.74.151': 1}, ('http://192.168.65.101/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '17/Feb/2013'): {'192.168.65.56': 11}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=all&admin=1', '17/Feb/2013'): {'192.168.12.61': 1}, ('http://callider/pause/index/pause/ajaxPause?pauseConfigId=&admin=0', '18/Feb/2013'): {'192.168.12.61': 3}}
        self.assertDictEqual(self.result, number_visits_for_resources)

    def test_all_accounts_by_showing(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts_by_showing_bytes = self.billing.add_all_accounts(self.data)[0]
        self.result_by_showing_bytes = {('192.168.65.56', '17/Feb/2013'): 385.0, ('192.168.12.61', '18/Feb/2013'): 25.0, ('192.168.12.61', '17/Feb/2013'): 37.0, ('192.168.65.56', '18/Feb/2013'): 105.0}
        self.assertDictEqual(self.result_by_showing_bytes, all_accounts_by_showing_bytes)

    def test_all_accounts_by_count(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts_by_showing_bytes = self.billing.add_all_accounts(self.data)[1]
        self.result_by_showing_bytes = {('192.168.65.56', '18/Feb/2013'): 54867085.0, ('192.168.65.56', '17/Feb/2013'): 222032195.0, ('192.168.12.61', '17/Feb/2013'): 20917641.0, ('192.168.12.61', '18/Feb/2013'): 7188117.0}
        self.assertDictEqual(self.result_by_showing_bytes, all_accounts_by_showing_bytes)

    def test_get_accounts_by_showing_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(data = self.data)
        result = {'192.168.65.56': 490.0, '192.168.12.61': 62.0}
        self.assertDictEqual(result, accounts)

    def test_get_accounts_by_count_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(data=self.data, arg=1)
        result = {'192.168.65.56': 276899280.0, '192.168.12.61': 28105758.0}
        self.assertDictEqual(result, accounts)

    def test_get_accounts_for_some_period_by_showing_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(initial_date="17/02/2013",
                                                  final_date="17/02/2013", data=self.data)
        result = {'192.168.65.56': 385.0, '192.168.12.61': 37.0}
        self.assertDictEqual(result, accounts)

    def test_get_accounts_for_some_period_by_count_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(initial_date="17/02/2013",
                                                  final_date="17/02/2013",
                                                  data=self.data, arg=1)
        result = {'192.168.12.61': 20917641.0, '192.168.65.56': 222032195.0}
        self.assertDictEqual(result, accounts)

    def test_get_accounts_for_some_ip_by_count_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(ip='192.168.12.61', data=self.data, arg=1)
        result = {'192.168.12.61': 28105758.0}
        self.assertDictEqual(result, accounts)

    def test_get_accounts_for_some_ip_by_showing_bytes(self):
        self.data.set_current_costs_file("Tests/valid_costs")
        costs = self.billing.add_costs_of_resources(self.data)
        self.data.set_costs_of_resources(costs)
        data_for_resources = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_bytes_for_resources(data_for_resources[0])
        self.data.set_number_visits_for_resources(data_for_resources[1])
        all_accounts = self.billing.add_all_accounts(self.data)
        self.data.set_accounts_by_count_bytes(all_accounts[1])
        self.data.set_accounts_by_showing_bytes(all_accounts[0])
        accounts = self.billing.get_some_accounts(ip='192.168.12.61', data=self.data, arg=0)
        result = {'192.168.12.61': 62.0}
        self.assertDictEqual(result, accounts)


if __name__ == "__main__":
    unittest.main()
