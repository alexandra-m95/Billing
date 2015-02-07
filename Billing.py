__author__ = 'alexandra'

import re
import os
import datetime
import subprocess
import urllib.parse
import shutil


class Billing:
    def __init__(self):
        """
        Инициализация регулярных выражений для поиска даты, ip, адреса ресурса, количества
        запрашиваемых байт в лог-файле.
        """
        self.ip_reg = re.compile("^(\d+\.\d+\.\d+\.\d+)")
        self.address_of_resource_reg = \
            re.compile(r'(?:] \"[\w]+ )(?P<urn>.*?)(?: .*?\".*?\")(?P<uri>.*?)\"')
        self.date_reg = re.compile("(?<=[\[])(.*?)(?=[:])")
        self.received_bytes_reg = re.compile("\d+(?=\n)")
        self.processed_lines = 0

    @staticmethod
    def check_changes_in_costs(data):
        """
        Проверяет, были ли сделаны изменения в файле стоимостей ресурсов. Дата последнего
        изменения и имя самого файла хранятся в файле "data".
        :param data: экземпляр класса data.
        :return: True - были изменения. False - изменений не было или файл теперь не существует.
        """
        costs_file = data.get_current_costs_file()
        if os.path.isfile(costs_file):
            last_change_costs = data.get_last_change_costs_file()
            if os.path.getmtime(costs_file) != last_change_costs:
                return True
        return False

    @staticmethod
    def check_processing_all_log_strs(data):
        """
        Проверяет, обработаны ли все строки лог-файла посредством сравнения общего количества
        строк и номера последней обработанной строки, которая хранится в файле data.
        :param data: экземпляр класса data.
        :return: True - не все строки обработаны, False - либо лог-файл больше не существует,
        либо обработаны все строки.
        """
        log_file = data.get_current_log_file()
        current_number_of_line = data.get_current_number_of_line()

        if os.path.isfile(log_file):
            number_of_lines = \
                int(subprocess.check_output(['wc', '-l',
                                             log_file]).decode(encoding="utf-8").split(" ")[0])
            if current_number_of_line != number_of_lines:
                return True
        return False

    def add_costs_of_resources(self, data):
        """
        Считывание стоимостей ресурсов из файла и добавление их в словарь(имя файла содержится
        в файле "data") Проводится проверка, является ли первый параметр url и является ли второй
        параметр положительным числом.
        :param data: экземпляр класса data.
        :return: словарь, содержащий стоимости ресурсов.
        :raise ValueError: поучение в качестве второго параметра из строки файлов стоимостей
        ресурсов не положительного числа.
        """
        costs_file = data.get_current_costs_file()
        input_reader = open(costs_file)
        costs_of_resources = {}
        for string in input_reader:
            split_file_string = string.split(" ")
            split_file_string = [string_param for string_param in split_file_string if string_param
                                 != ""]
            if len(split_file_string) != 2:
                return {}
            else:
                url_check = urllib.parse.urlparse(split_file_string[0].strip())
                if not url_check.scheme and url_check.path:
                    return {}
                try:
                    if float(split_file_string[1].strip()) < 0:
                        raise ValueError
                    else:
                        costs_of_resources[split_file_string[0].strip()] =\
                            float(split_file_string[1].strip())
                except ValueError:
                    return {}
        input_reader.close()
        self.add_all_accounts(data)
        return costs_of_resources


    def get_some_accounts(self, ip=None, initial_date="1/01/1970", final_date="1/01/2050", arg=0,
                          data=None):
        """
        Получение счета за весь или определенный период для всех или для определенного пользователя
        за факт показа байтов или за их количество.
        :param ip: ip-адрес пользователя. если значение None, то получаем счета для всех ip.
        :param initial_date: начальная дата периода, за который выдается счет.
        :param final_date: конечная дата, за который выдается счет.
        :param arg: 0 - получение счетов за факт показа байтов, 1 - за количество.
        :return: счета по заявленным критериям.
        """
        accounts = {}
        if len(data.get_costs_of_resources()) == 0 or data.get_current_log_file() == "":
            return accounts
        accounts = self.__get_accounts_by_date(initial_date, final_date, data)[arg]
        if ip is not None:
            if ip in accounts:
                accounts_sum = 0
                for acc_ip in accounts:
                    if acc_ip == ip:
                        accounts_sum += float(accounts[acc_ip])
                return {ip: accounts_sum}
            else:
                return {}
        else:
            return accounts

    @staticmethod
    def add_all_accounts(data):
        """
        Получение всех счетов для пользователей за весь период.
        :return: словари вида {(ip, дата) = счет за количество байт} и {(ip, дата) =
        счет за факт показа байтов}
        """
        accounts_by_count_bytes = {}
        accounts_by_showing_bytes = {}
        bytes_for_resources = data.get_count_bytes_for_resourсes()
        visits_for_resources = data.get_count_visits_for_resourсes()
        costs_of_resources = data.get_costs_of_resources()
        for addr_and_date in bytes_for_resources:
            for ip in bytes_for_resources.get(addr_and_date):
                if not addr_and_date[0] in costs_of_resources:
                    continue
                accounts_by_count_bytes[(ip, addr_and_date[1])] = \
                    accounts_by_count_bytes.get((ip, addr_and_date[1]), 0)
                accounts_by_showing_bytes[(ip, addr_and_date[1])] = \
                    accounts_by_showing_bytes.get((ip, addr_and_date[1]), 0)
                accounts_by_count_bytes[(ip, addr_and_date[1])] = \
                    float(accounts_by_count_bytes[(ip, addr_and_date[1])]) + \
                    int(bytes_for_resources[addr_and_date][ip]) *\
                    float(costs_of_resources[addr_and_date[0]])
                accounts_by_showing_bytes[(ip, addr_and_date[1])] = \
                    float(accounts_by_showing_bytes[(ip, addr_and_date[1])]) + \
                    float(costs_of_resources[addr_and_date[0]]) *\
                    int(visits_for_resources[addr_and_date][ip])
        return [accounts_by_showing_bytes, accounts_by_count_bytes]

    def add_bytes_and_visits_for_resources(self, data):
        """
        Добавление количества байтов и визитов для всех ресурсов. Происходит считывание
        лог-файла с той строки, до которой он был досчитан во время последнего использования
        программы. Составление двух словарей видов {(адрес ресурса, дата):{ip: количество байтов}} и
        {(адрес ресурса, дата):{ip: количество посещений}}
        :return: словари с байтами и визитами для ресурсов.
        """
        log_file = data.get_current_log_file()
        current_number_of_line = data.get_current_number_of_line()
        # Проверить без decode
        number_of_lines = int(subprocess.check_output(['wc', '-l', log_file]).decode(
            encoding="utf-8").split(" ")[0])
        bytes_for_resources = data.get_count_bytes_for_resourсes()
        visits_for_resources = data.get_count_visits_for_resourсes()
        if number_of_lines == current_number_of_line:
            return [bytes_for_resources, visits_for_resources]
        try:
            file_reader = open(log_file)
        except FileNotFoundError:
            return [bytes_for_resources, visits_for_resources]
        for i in range(current_number_of_line):
            file_reader.__next__()
        for i in file_reader:
            ip = self.ip_reg.search(i)
            address_of_resource = self.address_of_resource_reg.search(i)
            count_of_bytes = self.received_bytes_reg.search(i)
            date = self.date_reg.search(i)
            if ip is not None \
                    and address_of_resource is not None and count_of_bytes is not None and date\
                    is not None:
                ip = ip.group(1)
                address_of_resource = address_of_resource.group('uri') +\
                    address_of_resource.group('urn')
                count_of_bytes = count_of_bytes.group()
                date = date.group(1)
                bytes_for_resources[(address_of_resource, date)] = \
                    bytes_for_resources.get((address_of_resource, date), {ip: 0})
                bytes_for_resources[(address_of_resource, date)][ip] = \
                    bytes_for_resources[(address_of_resource, date)].get(ip, 0) + \
                    int(count_of_bytes)
                visits_for_resources[(address_of_resource, date)] = \
                    visits_for_resources.get((address_of_resource, date), {ip: 0})
                visits_for_resources[(address_of_resource, date)][ip] = \
                    visits_for_resources[(address_of_resource, date)].get(ip, 0) + 1
            self.processed_lines += 1
            if self.processed_lines % 500 == 0 and self.processed_lines != 0:
                data.set_number_visits_for_resources(visits_for_resources)
                data.set_number_bytes_for_resources(bytes_for_resources)
                data.set_current_number_of_line(current_number_of_line + self.processed_lines)
                shutil.copyfile("data", "data_copy")
        file_reader.close()
        return [bytes_for_resources, visits_for_resources]

    @staticmethod
    def __get_accounts_by_date(initial_date, final_date, data):
        """
        Получение счетов за определенный период.
        :param initial_date: начальная дата периода.
        :param final_date: конечная дата периода.
        :param data: экземпляр класса data.
        :return: счета по факту показа байтов и по количеству байтов.
        """
        accounts_by_sh_bts_by_date = {}
        accounts_by_cnt_bts_by_date = {}
        accounts_by_count_bytes = data.get_accounts_by_count_bytes()
        accounts_by_showing_bytes = data.get_accounts_by_showing_bytes()
        initial_date = datetime.datetime.strptime(initial_date, "%d/%m/%Y")
        final_date = datetime.datetime.strptime(final_date, "%d/%m/%Y")
        for i in accounts_by_showing_bytes:
            current_date = datetime.datetime.strptime(i[1], "%d/%b/%Y")
            if initial_date <= current_date <= final_date:
                accounts_by_sh_bts_by_date[i[0]] = accounts_by_sh_bts_by_date.get(i[0], 0)
                accounts_by_sh_bts_by_date[i[0]] += float(accounts_by_showing_bytes[i])
                accounts_by_cnt_bts_by_date[i[0]] = accounts_by_cnt_bts_by_date.get(i[0], 0)
                accounts_by_cnt_bts_by_date[i[0]] += float(accounts_by_count_bytes[i])
        return [accounts_by_sh_bts_by_date, accounts_by_cnt_bts_by_date]
