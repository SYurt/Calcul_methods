import sys
import csv
import numpy as np
from sympy import symbols, sympify
from sympy.utilities.lambdify import lambdify
import math
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem
from Unlinear_eq_ import Ui_Form
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class UnlinearEquationSolver(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initializeUI()
        np.set_printoptions(precision=3)
        # self.show()
        self.setGeometry(100, 100, 860, 600)
        self.result = np.empty((0, 0), dtype='float')

    def initializeUI(self):

        # Знайти віджет QGraphicsView за ім'ям ("graphicsView")
        self.ui.graphicsView = self.findChild(QWidget, "graphicsView")

        # Створити віджет графіка Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Отримати поточні вісі для побудови графіка
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self.ui.graphicsView)
        layout.addWidget(self.canvas)
        # self.ui.horizontalLayout_8.addWidget(self.canvas)

        #validation
        self.ui.func_entry.setPlaceholderText("Введіть формулу в нотації Python")
        regex1 = QRegularExpression("-?[0-9]+\.?[0-9]*")
        self.ui.a_entry.setValidator(QRegularExpressionValidator(regex1))
        self.ui.b_entry.setValidator(QRegularExpressionValidator(regex1))
        regex2 = QRegularExpression("[0-9]+")
        self.ui.initial_guess_entry.setValidator(QRegularExpressionValidator(regex2))
        regex3 = QRegularExpression("[0-9]+\.?[0-9]*")
        self.ui.precisionBis_entry.setValidator(QRegularExpressionValidator(regex3))
        self.ui.precisionNew_entry.setValidator(QRegularExpressionValidator(regex3))

        # Add signal/slot connections for buttons
        self.ui.plot_button.clicked.connect(self.run_plot)
        self.ui.iterations_button.clicked.connect(self.iterations)
        self.ui.bisection_button.clicked.connect(self.bisection)
        # clear table
        self.ui.button_clear.clicked.connect(self.clear_table)
        # save to file
        self.ui.save_button.clicked.connect(self.save_table_file)

    def f(self, x):
        pass
        # func_str = self.func_entry.text()
        # func = lambda x: eval(func_str)

        # return 2*x - math.log(x) - 4
        # return math.log((x+1)/(x-1))-2*x

    def run_plot(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = 'log((x+1)/(x-1))-2*x'
        f = self.convert_to_func(func_text)
        self.plot(f)

    def iterations(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = 'log((x+1)/(x-1))-2*x'
        f = self.convert_to_func(func_text)
        self.run_iterations(f)

    def bisection(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = 'log((x+1)/(x-1))-2*x'
        f = self.convert_to_func(func_text)
        self.run_bisection(f)

    def convert_to_func(self, func_text):
        try:
            # variables in math expressions
            x = symbols('x')
            y = symbols('y')
            z = symbols('z')
            # convert text to SymPy object
            expression = sympify(func_text)
            # function from expression, use numpy to optimize work
            # with NumPy objects if variables or result are arrays
            return lambdify(x, expression, 'numpy')
        except Exception as e:
            self.ui.result_label.setText(f'Помилка у перетворені тексту в функцію: {str(e)}')

    # Метод ітерацій
    def run_iterations(self, f):
        a = float(self.ui.a_entry.text())
        b = float(self.ui.b_entry.text())
        if math.isnan(f(a)) or math.isnan(f(b)):
            self.ui.result_label.setText(f'Некоректне введення відрізку')
        self.result = np.empty((0, 0), dtype='float')
        method = 'ітерацій'
        try:
            iterations_num = int(self.ui.initial_guess_entry.text())

            if self.ui.multiple_roots_button.isChecked():
                self.iterations_multiple_root(f, a, b, iterations_num)
            else:
                self.iterations_single_root(f, a, b, iterations_num)

            print(self.result)
            self.ui.result_label.setText(f"Результат (Метод ітерацій): {np.array2string(self.result, precision=3, separator=', ')}")
            # for root in self.result:
            #     self.update_table(self.ui.table_iterations, iterations_num, root, f(root))
            self.update_table(self.ui.table_iterations, iterations_num, self.result, f(self.result))
            self.plot_result(f, self.result, method)
        except ValueError:
            self.ui.result_label.setText("Помилка: Некоректне введення відрізку")

     # Метод ітерацій пошук декількох коренів
    def iterations_multiple_root(self, f, a, b, iterations_num):
        try:
            dx = (b - a)/iterations_num
            for i in range(iterations_num):
                sign = f(a + dx*i)*f(a + dx*(i+1))
                if sign < 0:
                    self.result = np.append(self.result, (a+a+dx*i+dx*i+dx)/2)
                if sign == 0:
                    self.result = np.append(self.result, a + dx*i) if f(a + dx*i) == 0 else np.append(self.result, a + dx*(i+1))
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

    # Метод ітерацій пошук одного кореня
    def iterations_single_root(self, f, a, b, iterations_num):
        try:
            dx = (b - a)/iterations_num
            for i in range(iterations_num):
                sign = f(a + dx*i)*f(a + dx*(i+1))
                if sign < 0:
                    # result = (a+a+dx*i+dx*i+dx)/2
                    self.result = np.append(self.result, (a+a+dx*i+dx*i+dx)/2)
                    break
                if sign == 0:
                    # result = (a + dx*i) if f(a + dx*i) == 0 else (a + dx*(i+1))
                    self.result = np.append(self.result, a + dx*i) if f(a + dx*i) == 0 else np.append(self.result, a + dx*(i+1))
                    break
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

    # Метод дихотомії
    def run_bisection(self, f):
        self.result = np.array([], dtype='float')
        a = float(self.ui.a_entry.text())
        b = float(self.ui.b_entry.text())
        eps = float(self.ui.precisionBis_entry.text())
        # if math.isnan(f(a)) or math.isnan(f(b)):
        #     self.ui.result_label.setText(f'Некоректне введення відрізку')
        try:
            if self.ui.multiple_roots_button.isChecked():
                # рекурсивний пошук декількох коренів
                self.bisection_multiple_root(f, a, b)
            else:
                # для пошуку одного кореня
                self.bisection_single_root(f, a, b, eps)

            print(self.result)
            method = 'дихотомії'
            self.ui.result_label.setText(f"Результат (Метод дихотомії): {np.array2string(self.result, precision=3, separator=', ')}")
            self.update_table(self.ui.table_bisection, eps, self.result, f(self.result))
            self.plot_result(f, self.result, method)
        except ValueError:
            self.ui.result_label.setText("Помилка: Некоректне введення відрізку")

    # Метод дихотомії для пошуку одного кореня
    def bisection_single_root(self, f, a, b, eps):
        root = False
        try:
            while (b-a) >= eps:
                x = (a+b)/2
                sign = f(a)*f(x)
                if math.isnan(sign):
                    return
                if sign == 0:
                    if f(a) == 0:
                        root = True
                    # result = a if f(a) == 0 else x
                    break
                if sign < 0:
                    b = x
                else:
                    a = x
            # result = (a+b)/2 if not root else a
            self.result = np.append(self.result, (a+b)/2) if not root else np.append(self.result, a)
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')


    # Метод дихотомії, рекурсивний пошук декількох коренів
    def bisection_multiple_root(self, f, a, b):
        eps = float(self.ui.precisionBis_entry.text())
        try:
            if (b-a) <= eps:
                if f(a)*f(b) < 0:
                    self.result = np.append(self.result, (a+b)/2)
                if f(a)*f(b) == 0:
                    self.result = np.append(self.result, a) if f(a) == 0 else np.append(self.result, b)
                return
            x = (a+b)/2
            self.bisection_multiple_root(f, a, x)
            self.bisection_multiple_root(f, x, b)
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')


    def update_table(self, table, param, result, func_value):
        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, 0, QTableWidgetItem(str(param)))
        table.setItem(row_position, 1, QTableWidgetItem(f"{np.array2string(result, precision=3, separator=', ')}"))
        table.setItem(row_position, 2, QTableWidgetItem(f"{np.array2string(func_value, precision=3, separator=', ')}"))

    def plot(self, func):
            a = float(self.ui.a_entry.text())
            b = float(self.ui.b_entry.text())
            x = np.linspace(a, b, 500)
            y = []
            try:
                y = [func(xi) for xi in x]
            except ZeroDivisionError as e:
                self.ui.result_label.setText(f'Помилка: {e}')

            # self.ax.axhline(0, color='black')
            # self.ax.axvline(0, color='black')

            # графік у вікні matplotlib
            plt.figure()
            plt.plot(x, y, label=self.ui.func_entry.text())
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title(f'Графік функції')
            plt.legend()
            plt.grid(True)
            plt.show()

    def plot_result(self, func, result, method):
        a = float(self.ui.a_entry.text())
        b = float(self.ui.b_entry.text())
        x = np.linspace(a, b, 500)
        y = []
        try:
            y = [func(xi) for xi in x]
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

        # графік canvas у вікні інтерфейсу
        self.ax.clear()
        self.ax.plot(x, y, label= self.ui.func_entry.text())
        self.ax.scatter(result, func(result), color='red', label='Корінь', marker='o')
        self.ax.axhline(0, color='black')
        self.ax.axvline(0, color='black')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.ax.set_title(f'Оптимізація методом {method}')
        self.ax.legend()
        self.canvas.draw()

        # графік у вікні matplotlib
        # plt.figure()
        # plt.plot(x, y, label='Функція')
        # plt.scatter(result, func(result), color='red', label='Корінь', marker='o')
        # plt.xlabel('x')
        # plt.ylabel('y')
        # plt.title(f'Оптимізація методом {method}')
        # plt.legend()
        # plt.grid(True)
        # plt.show()

    def clear_table(self):
        current_tab_widget = self.ui.tabWidget.currentWidget()
        table_widget = current_tab_widget.findChild(QTableWidget)
        table_widget.setRowCount(0)

    def save_table_file(self):
        # Поточний індекс вкладки
        current_tab_index = self.ui.tabWidget.currentIndex()

        # Отримати поточну вкладку за індексом
        current_tab = self.ui.tabWidget.widget(current_tab_index)

        # Отримати об'ект QTableWidget на поточній вкладці
        table_widget = current_tab.findChild(QTableWidget)

        # Отримуємо дані таблиці
        data = []
        for row in range(table_widget.rowCount()):
             # додати назву методу
            row_data = [self.ui.tabWidget.tabText(current_tab_index)]
            for column in range(table_widget.columnCount()):
                item = table_widget.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        # Відкрити діалогове вікно для вибору файлу та отримати шлях
        file_name, _ = QFileDialog.getSaveFileName(self, "Збереження в файл", "equation_resolutions.csv", "CSV Files (*.csv);;All Files (*)")

        if file_name:
            try:
                with open(file_name, 'a', newline='', encoding="utf-16") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for row_data in data:
                        csv_writer.writerow(row_data)
                QMessageBox.information(self, "Успех", "Таблица успешно сохранена в файл.")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Помилка при збереженні файла: {str(e)}")
def main():
    app = QApplication(sys.argv)
    window = UnlinearEquationSolver()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
