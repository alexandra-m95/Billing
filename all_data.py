__author__ = 'alexandra'
import json
import shutil

class Data:
    def __init__(self):
        self.data = {}
        shutil.copyfile("default_data", "data")
        with open("data") as f:
            self.data = json.load(f)


    def set_current_log_file(self, file_name):
        self.data['current_log_file'] = str(file_name)
        self.set_current_number_of_line(0)
        self.set_number_bytes_for_resources({})
        self.set_number_visits_for_resources({})
        self.set_accounts_by_count_bytes({})
        self.set_accounts_by_showing_bytes({})
        self.write_to_file()

    def set_current_number_of_line(self, number_of_line):
        self.data['current_number_of_line'] = str(number_of_line)
        self.write_to_file()

    def set_current_costs_file(self, file_name):
        self.data['current_costs_file'] = str(file_name)
        self.set_costs_of_resources({})
        self.write_to_file()

    def set_last_change_costs_file(self, change_time):
        self.data['last_change_costs_file'] = str(change_time)
        self.write_to_file()

    def set_costs_of_resources(self, costs):
        self.data['costs_of_resources'] = costs
        self.set_accounts_by_showing_bytes({})
        self.set_accounts_by_count_bytes({})
        self.write_to_file()

    def set_accounts_by_showing_bytes(self, accounts):
        self.data['accounts_by_showing_bytes'] = eval(str(accounts).replace('(', '"(').replace(')', ')"'))
        self.write_to_file()

    def set_accounts_by_count_bytes(self, accounts):
        self.data['accounts_by_count_bytes'] = eval(str(accounts).replace('(', '"(').replace(')', ')"'))
        self.write_to_file()

    def set_number_bytes_for_resources(self, number):
        self.data['number_bytes_for_resources'] = eval(str(number).replace('(', '"(').replace(')', ')"'))
        self.write_to_file()

    def set_number_visits_for_resources(self, number):
        self.data['number_visits_for_resources'] = eval(str(number).replace('(', '"(').replace(')', ')"'))
        self.write_to_file()

    def get_current_log_file(self):
        return self.data['current_log_file']

    def get_current_number_of_line(self):
        return int(self.data['current_number_of_line'])

    def get_current_costs_file(self):
        return self.data['current_costs_file']

    def get_last_change_costs_file(self):
        return float(self.data['last_change_costs_file'])

    def get_costs_of_resources(self):
        return self.data['costs_of_resources']

    def get_accounts_by_showing_bytes(self):
        return eval(str(self.data['accounts_by_showing_bytes']).replace('"(', '(').replace(')"',')'))

    def get_accounts_by_count_bytes(self):
        return eval(str(self.data['accounts_by_count_bytes']).replace('"(', '(').replace(')"',')'))

    def get_count_bytes_for_resourсes(self):
        return eval(str(self.data['number_bytes_for_resources']).replace('"(', '(').replace(')"',')'))

    def get_count_visits_for_resourсes(self):
        return eval(str(self.data['number_visits_for_resources']).replace('"(', '(').replace(')"',')'))

    def write_to_file(self):
        with open("data", "w") as f:
            json.dump(self.data, f, indent=0)
