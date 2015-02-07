#Мои модули
from all_data import Data
from Billing import Billing

import os
import subprocess
import locale
from threading import Thread


from gi.repository import Gtk, GObject


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
GObject.threads_init()


class BillingWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Биллинг")
        self.set_border_width(10)
        self.set_resizable(False)
        self.data = Data()
        self.billing = Billing()
        self.initial_year_spin = Gtk.SpinButton()
        self.initial_month_spin = Gtk.SpinButton()
        self.initial_day_spin = Gtk.SpinButton()
        self.final_year_spin = Gtk.SpinButton()
        self.final_month_spin = Gtk.SpinButton()
        self.final_day_spin = Gtk.SpinButton()
        self.add(self.add_widgets())
        self.show_all()
        if self.billing.check_changes_in_costs(self.data):
            self.changed_costs_question()
            costs_file = self.data.get_current_costs_file()
            self.data.set_last_change_costs_file(os.path.getmtime(costs_file))
        if self.billing.check_processing_all_log_strs(self.data):
            self.log_info()

    def changed_costs_question(self):
        """
        Выдается сообщение об изменении стоимостей ресурсов в текущем файле. Предлагается
        применить их.

        """
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO,
                                   "В файле стоимостей ресурсов произошли изменения")
        dialog.format_secondary_text("Изменить текущие стоимости?")
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            costs = self.billing.add_costs_of_resources(self.data)
            if costs == {}:
                self.show_error(True)
            else:
                self.data.set_costs_of_resources(costs)
                accounts = self.billing.add_all_accounts(self.data)
                self.data.set_accounts_by_showing_bytes(accounts[0])
                self.data.set_accounts_by_count_bytes(accounts[1])
        dialog.destroy()

    def log_info(self):
        """
        Выдается сообщение в случае добавления строк в лог-файл.

        """
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   "В лог файле произошли изменения.")
        dialog.format_secondary_text("Возможно были добавлены новые записи "
                                     "или чтение не было завершено во время "
                                     "предыдущей работы программы.")
        dialog.run()
        dialog.destroy()

    def add_widgets(self):
        """
        Метод создает контейнер и вызывает методы для
        добавления всех виджетов в него.
        :return: контейнер с виджетами.
        """
        fixing_box = Gtk.Fixed()
        fixing_box.add(self.add_menu_bar())
        fixing_box.put(self.add_text_view(), 380, 0)
        fixing_box.put(self.add_other_widgets(), 0, 0)
        ok_button = Gtk.Button("OK")
        ok_button.set_size_request(110, 35)
        ok_button.connect("clicked", self.on_ok_clicked)
        fixing_box.put(ok_button, 0, 380)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_size_request(590, 30)
        fixing_box.put(self.progressbar, 130, 383)
        return fixing_box

    def add_text_view(self):
        """
        Создает контейнер, в который добавляется рамка с другим контейнером.
        В него добавляется многострочный текстовый редактор с полосами прокрутки.
        :return: рамка с контейнером, который содержит многострочный текстовый редактор.
        """
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_buffer = self.text_view.get_buffer()
        box = Gtk.Box()
        scrolled_window = Gtk.ScrolledWindow()
        frame = Gtk.Frame()
        scrolled_window.set_size_request(350, 360)
        scrolled_window.add(self.text_view)
        box.pack_start(scrolled_window, True, True, 0)
        frame.add(box)
        return frame


    def add_menu_bar(self):
        """
        Создает меню.

        :return: меню.
        """
        menu_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        help_menu = Gtk.Menu()
        file_item = Gtk.MenuItem("Файл")
        help_item = Gtk.MenuItem("Помощь")
        costs_item = Gtk.MenuItem("Файл стоимости")
        log_item = Gtk.MenuItem("Лог файл")
        exit_item = Gtk.MenuItem("Выход")
        information_item = Gtk.MenuItem("О задаче")
        self.save_item = Gtk.MenuItem("Сохранить")
        self.save_as_item = Gtk.MenuItem("Сохранить как..")
        self.save_item.set_sensitive(False)
        self.save_as_item.set_sensitive(False)
        log_item.connect_object("activate", self.show_select, "log_win", True)
        costs_item.connect_object("activate", self.show_select, "file.costs", False)
        # self.save_as_item.connect_object("activate", self.show_file_save_as, "file.save")
        exit_item.connect_object("activate", self.destroy, "exit")
        information_item.connect_object("activate", self.show_help, "file.help")
        file_menu.append(costs_item)
        file_menu.append(log_item)
        file_menu.append(self.save_item)
        file_menu.append(self.save_as_item)
        file_menu.append(exit_item)
        help_menu.append(information_item)
        file_item.set_submenu(file_menu)
        help_item.set_submenu(help_menu)
        menu_bar.append(file_item)
        menu_bar.append(help_item)
        return menu_bar

    def add_other_widgets(self):
        """
        Создаются все виджеты.

        :return:
        """
        fixed = Gtk.Fixed()
        self.checkbutton = Gtk.CheckButton("Считать полностью")
        self.checkbutton.set_active(True)
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_size_request(200, 20)
        self.ip_entry.set_max_length(20)
        self.show_bytes_button = Gtk.RadioButton.new_with_label_from_widget(None, "по факту соединения")
        self.count_bytes_button = Gtk.RadioButton.new_with_label_from_widget(self.show_bytes_button, "по количеству байтов")
        self.all_ip_button = Gtk.RadioButton.new_with_label_from_widget(None, "для всех IP")
        self.some_ip_button = Gtk.RadioButton.new_with_label_from_widget(self.all_ip_button, "выбрать IP")
        self.all_period_button = Gtk.RadioButton.new_with_label_from_widget(None, "за весь период")
        self.some_period_button = Gtk.RadioButton.new_with_label_from_widget(self.all_period_button, "выбрать период")
        self.some_period_button.connect("toggled", self.add_sensitives_on_spin, True)
        self.all_period_button.connect("toggled", self.add_sensitives_on_spin, False)
        entry = Gtk.Entry()
        entry.set_max_length(50)
        entry.set_editable(False)
        from_label = Gtk.Label("C:")
        to_label = Gtk.Label("По:")
        initial_year_adjustment = Gtk.Adjustment(2000, 2000, 2030, 1, 10, 0)
        initial_month_adjustment = Gtk.Adjustment(1, 1, 12, 1, 10, 0)
        initial_day_adjustment = Gtk.Adjustment(1, 1, 31, 1, 10, 0)
        final_year_adjustment = Gtk.Adjustment(2000, 2000, 2030, 1, 10, 0)
        final_month_adjustment = Gtk.Adjustment(1, 1, 12, 1, 10, 0)
        final_day_adjustment = Gtk.Adjustment(1, 1, 31, 1, 10, 0)
        self.initial_year_spin.set_adjustment(initial_year_adjustment)
        self.initial_month_spin.set_adjustment(initial_month_adjustment)
        self.initial_day_spin.set_adjustment(initial_day_adjustment)
        self.final_year_spin.set_adjustment(final_year_adjustment)
        self.final_month_spin.set_adjustment(final_month_adjustment)
        self.final_day_spin.set_adjustment(final_day_adjustment)
        self.add_sensitives_on_spin(0, False)
        fixed.put(self.checkbutton, 5, 10)
        fixed.put(self.show_bytes_button, 5, 60)
        fixed.put(self.count_bytes_button, 185, 60)
        fixed.put(self.all_ip_button, 5, 110)
        fixed.put(self.some_ip_button, 185, 110)
        fixed.put(self.all_period_button, 0, 230)
        fixed.put(self.some_period_button, 185, 230)
        fixed.put(self.ip_entry, 10, 170)
        fixed.put(from_label, 0, 275)
        fixed.put(self.initial_year_spin, 25, 270)
        fixed.put(self.initial_month_spin, 140, 270)
        fixed.put(self.initial_day_spin, 255, 270)
        fixed.put(to_label, 0, 335)
        fixed.put(self.final_year_spin, 25, 330)
        fixed.put(self.final_month_spin, 140, 330)
        fixed.put(self.final_day_spin, 255, 330)
        fixed.put(Gtk.Label("--"), 131, 275)
        fixed.put(Gtk.Label("--"), 245, 275)
        fixed.put(Gtk.Label("--"), 131, 335)
        fixed.put(Gtk.Label("--"), 245, 335)
        return fixed

    def show_select(self, _, log):
        """
        Показывает окно добавления либо файла стоимосте ресурсов, либо лог-файла.
        :param _:
        :param log: Если лог == True, то будет выдано окно выбора лог-файла. Иначе -
        выбора стоимостей ресурсов.
        """
        if log:
            title = "Выбор лог файла"
            entry_text = self.data.get_current_log_file()
        else:
            title = "Выбор файла стоимости"
            entry_text = self.data.get_current_costs_file()
        dialog = Gtk.Dialog(title, self, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_size(250, 100)
        fixed = Gtk.Fixed()
        add_button = Gtk.Button("Открыть")
        self.select_file_entry = Gtk.Entry()
        self.select_file_entry.set_size_request(300, 30)
        self.select_file_entry.set_editable(False)
        self.select_file_entry.set_text(entry_text)
        self.filename = entry_text
        add_button.connect("clicked", self.show_file_open, log)
        fixed.put(self.select_file_entry, 0, 0)
        fixed.put(add_button, 305, 0)
        box = dialog.get_content_area()
        box.add(fixed)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            if log:
                self.data.set_current_log_file(self.filename)
                self.billing.processed_lines = 0
            else:
                self.data.set_current_costs_file(self.filename)
                costs = self.billing.add_costs_of_resources(self.data)
                if costs == {}:
                    self.show_error(True)
                else:
                    self.data.set_costs_of_resources(costs)
        dialog.destroy()

    def show_file_open(self, _, __):
        """
        Показывает окно выбора файла.
        :param widget: ссылка на объект, к которому был применен сигнал.
        """
        dialog = Gtk.FileChooserDialog("Выберите файл", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        text_filter = Gtk.FileFilter()
        java_filter = Gtk.FileFilter()
        text_filter.set_name("Текстовые файлы")
        text_filter.add_mime_type("text/plain")
        dialog.add_filter(text_filter)
        dialog.add_filter(java_filter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.filename = dialog.get_filename()
            self.select_file_entry.set_text(self.filename)
        dialog.destroy()

    def show_error(self, costs_format_error):
        """
        Показывает окно в случае ошибки: либо неверный формат файла стоимостей ресурсов,
        либо отсутствие стоимостей ресурсов.
        :param costs_format_error: True - необходимо выдать окно неверного формата.
        False - отсутствия стоимостей.
        """
        if costs_format_error:
            text = "Неверный формат файла стоимостей ресурсов."
            secondary_text = ("В файле должны быть только пары: адрес ресурса и его "
                              "стоимость(положительное число) через пробел. Каждая пара "
                              "на новой строке.")
        else:
            text = "Не были добавлены стоимости ресурсов"
            secondary_text = ""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.CANCEL, text)
        dialog.format_secondary_text(secondary_text)
        dialog.run()
        dialog.destroy()

    @staticmethod
    def show_help(_):
        """
        Вызывается через меню после нажатия на "Help" --> "О задаче".
        :param widget: ссылка на объект, к которому был применен сигнал.
        """
        dialog = Gtk.Dialog("О задаче", None, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_size_request(200, 400)
        dialog.set_resizable(False)
        box = Gtk.Box()
        scrolledwindow = Gtk.ScrolledWindow()
        text_view = Gtk.TextView()
        text_buffer = text_view.get_buffer()
        text_view.set_editable(False)
        text_view.set_wrap_mode(True)
        scrolledwindow.set_size_request(330, 400)
        scrolledwindow.add(text_view)
        frame = Gtk.Frame()
        box.pack_start(scrolledwindow, True, True, 0)
        frame.add(box)
        dialog.vbox.pack_start(frame, True, False, 0)
        with open("help") as helps:
            text_buffer.set_text(helps.read())
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
        dialog.destroy()
    @staticmethod
    def destroy(widget):
        """
        Уничтожает диалоговые окна.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        """
        Gtk.main_quit()

    def add_sensitives_on_spin(self, _, sens):
        """
         Вызывается в случае, если нажимаем на кнопку "за весь период"  или "за определенный
         период". В первом случае виджеты настройки периода становятся неактивными, во втором -
         активными.
        :param _:
        :param sens: True - виджеты становятся активными. False - виджеты становятся неактивными.
        """
        self.initial_year_spin.set_sensitive(sens)
        self.initial_month_spin.set_sensitive(sens)
        self.initial_day_spin.set_sensitive(sens)
        self.final_year_spin.set_sensitive(sens)
        self.final_month_spin.set_sensitive(sens)
        self.final_day_spin.set_sensitive(sens)

    def on_ok_clicked(self, _):
        """
        В случае остсутсвия стоимостей ресурсов вызывает метод показа сообщения об ошибке.
        Если кнопка "считать файл посностью" активна, то выясняется последняя обработанная строка
        и начинается анализ лога с неё. Если не активна, то счета байты и визиты для ресурсов
        не дополняются. Анализ происходит в отдельном потоке. В текущем отображается процесс
        обработки лог-файла. После обработки отображаются счета в соответсвиями с текущими
        состояниями виджетов настроек.
        :param _:
        :return: None.
        """
        if self.data.get_costs_of_resources() == {}:
            self.show_error(False)
            return
        if self.checkbutton.get_active() and self.billing.check_processing_all_log_strs(self.data):
            log_file = self.data.get_current_log_file()
            number_of_lines = int(subprocess.check_output(['wc', '-l', log_file]).decode(encoding="utf-8").split(" ")[0])
            current_line = self.data.get_current_number_of_line()
            self.progressbar.set_fraction(current_line/number_of_lines)
            calculations = LongCalculationsThread(self.billing, self.data)
            calculations.start()
            old_processed_lines = 0
            const_current_line = current_line
            while current_line < number_of_lines:
                if self.billing.processed_lines != old_processed_lines:
                    current_line = const_current_line + self.billing.processed_lines
                    old_processed_lines = self.billing.processed_lines
                    self.progressbar.set_fraction(current_line/number_of_lines)
                    while Gtk.events_pending():
                        Gtk.main_iteration()
            self.data.set_current_number_of_line(number_of_lines)
            all_accounts = self.billing.add_all_accounts(self.data)
            self.data.set_accounts_by_showing_bytes(all_accounts[0])
            self.data.set_accounts_by_count_bytes(all_accounts[1])
        arg = 0
        ip = None
        initial_date = "1/01/1970"
        final_date = "1/01/2050"
        if self.count_bytes_button.get_active():
            arg = 1
        if self.some_ip_button.get_active():
            ip = self.ip_entry.get_text()
        if self.some_period_button.get_active():
            init_year = self.initial_year_spin.get_value()
            init_month = self.initial_month_spin.get_value()
            init_day = self.initial_day_spin.get_value()
            final_year = self.final_year_spin.get_value()
            final_month = self.final_month_spin.get_value()
            final_day = self.final_day_spin.get_value()
            initial_date = "{0}/{1}/{2}".format(int(init_day), int(init_month), int(init_year))
            final_date = "{0}/{1}/{2}".format(int(final_day), int(final_month), int(final_year))
        accounts = self.billing.get_some_accounts(ip, initial_date, final_date, arg, self.data)
        result = ""
        for i in accounts:
            result += str(i) + " - " + str(accounts.get(i)) + "\n"
        self.text_buffer.set_text(result)
        self.save_item.set_sensitive(True)
        self.save_as_item.set_sensitive(True)


class LongCalculationsThread(Thread):
    def __init__(self, billing, data):
        Thread.__init__(self)
        self.billing = billing
        self.data = data

    def run(self):
        k = self.billing.add_bytes_and_visits_for_resources(self.data)
        self.data.set_number_visits_for_resources(k[0])
        self.data.set_number_bytes_for_resources(k[1])
        return True


if __name__ == "__main__":
    win = BillingWindow()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()