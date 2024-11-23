"""
GUI CRUD app for keeping track of student loan money

TODO:
    * Popup menu for adding rows
    * Popup menu for editing rows
    * Popup - Are you sure you want to delete this?
    * menu for SQL backup navigation
                * get rid of top edit panel but ...
        * make it popup when clicking the add/edit button

    * backup database on app exit
"""

import tkinter as tk
from tkinter import ttk
from os import environ as env

from MySQL import connection, selectIncome, selectExpenses, incomeTotal, expenseTotal, editRow


class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.focus_force()
        self.root.title("Student Loan CRUD App")  # Window name
        self.root.geometry('470x650')
        self.root.resizable(width=False, height=False)

        # Title frame
        self.title_frame = tk.Frame(self.root)
        self.title_frame.pack(anchor='n')
        tk.Label(self.title_frame, text='Tracking Student Loan Income & Expenses\n', font=('Inter', 18, 'bold')).pack(expand=False)

        # Content frame         width=405
        self.content_frame = tk.Frame(self.root, padx=20)
        self.content_frame.pack(expand=True, fill='both')

        # self.table = None
        self.income_table = None
        self.expense_table = None
        self.input_date = None
        self.input_total = None
        self.input_amount = None
        self.input_details = None
        self.btnFrame = None


        # Temp
        self.selectedTable = None
        self.selectedID = None
        self.selectedDate = None
        self.selectedDetails = None
        self.selectedAmount = None

        env['table'] = str(self.selectedTable)
        env['id'] = str(self.selectedID)
        env['date'] = str(self.selectedDate)
        env['details'] = str(self.selectedDetails)
        env['amount'] = str(self.selectedAmount)

        # Display table windows
        # TODO DISPLAY REMAINING $
        tk.Label()
        self.incomeTable()
        # self.summaryPanel()
        self.expensesTable()

    def summaryPanel(self):
        # MySQL queries
        conn = connection()
        total_income = incomeTotal(conn)
        total_spent = expenseTotal(conn)
        unspent = float(total_income - total_spent)
        percentage = round((float(float(unspent) / float(total_income)) * 100), 2)

        # Shift row - 1 to remove blank row above this row
        tk.Label(self.content_frame, text=f'Total Loaned:     $ {total_income}').grid(row=1, column=1)
        tk.Label(self.content_frame, text=f'Total Spent:     $ {total_spent}').grid(row=2, column=1)
        tk.Label(self.content_frame, text=f'Total Unspent:    $ {unspent}').grid(row=1, column=2)
        tk.Label(self.content_frame, text=f'                         % {percentage}').grid(row=2, column=2)

    def incomeTable(self):
        tk.Label(self.content_frame, text=f'\nIncome: ${incomeTotal(connection()):,.2f}', font=('Inter', 16, 'bold')).grid(row=3, column=1)

        self.income_table = ttk.Treeview(self.content_frame, show='headings', columns=('ID', 'Date', 'Details', 'Amount'), height=5)
        self.income_table.heading('Date', text='Date')
        self.income_table.heading('Amount', text='Amount')
        self.income_table.heading('Details', text='Details')
        self.income_table.column('ID', width=10)
        self.income_table.column('Date', width=90)
        self.income_table.column('Details', width=250)
        self.income_table.column('Amount', width=80)

        if connection() is not None:
            data = selectIncome(connection())
            for row in data:
                self.income_table.insert("", tk.END, values=row)
            connection().close()

        self.income_table.grid(row=4, column=1, columnspan=5)
        self.income_table.bind('<ButtonRelease-1>', lambda event: self.selectItem(event, 'Income'))

        # Buttons
        self.btnFrame = ttk.Frame(self.content_frame)
        self.btnFrame.grid(row=5, column=1, columnspan=4)
        tk.Button(self.btnFrame, text="Add Row", command=lambda: self.addPopup('Income')).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Edit Row", command=lambda: self.editIncomePopup()).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Delete Row", command=lambda: self.deletePopup('Income')).pack(side=tk.LEFT, padx=5, pady=5)

    def expensesTable(self):
        tk.Label(self.content_frame, text='Expenses', font=('Inter', 16, 'bold')).grid(row=6, column=1)

        # Define the table
        self.expense_table = ttk.Treeview(self.content_frame, show='headings', columns=('ID', 'Date', 'Details', 'Amount'))
        self.expense_table.heading('Date', text='Date')
        self.expense_table.heading('Amount', text='Amount')
        self.expense_table.heading('Details', text='Details')
        self.expense_table.column('ID', width=10)
        self.expense_table.column('Date', width=90)
        self.expense_table.column('Details', width=250)
        self.expense_table.column('Amount', width=80)

        # Fill the table w/ data
        if connection() is not None:
            data = selectExpenses(connection())
            for row in data:
                self.expense_table.insert("", tk.END, values=row)
            connection().close()

        self.expense_table.grid(row=7, column=1, columnspan=4)
        self.expense_table.bind('<ButtonRelease-1>', lambda event: self.selectItem(event, 'Expenses'))

        # Interaction buttons
        self.btnFrame = ttk.Frame(self.content_frame)
        self.btnFrame.grid(row=8, column=1, columnspan=4)
        tk.Button(self.btnFrame, text="Add Row", command=lambda: self.addPopup('Expenses')).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Edit Row", command=lambda: self.editExpensePopup()).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Delete Row", command=lambda: self.deletePopup('Expenses')).pack(side=tk.LEFT, padx=5, pady=5)

    def editIncomePopup(self):
        if env['table'] == 'Income':
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Entry")
            edit_window.geometry('625x175')

            # Populate entries with selected item details
            tk.Label(edit_window, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Amount").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Details").grid(row=0, column=2, sticky="w", padx=5, pady=5)

            self.input_date = tk.Entry(edit_window)
            self.input_date.grid(row=0, column=1, padx=5, pady=5)
            self.input_date.insert(0, env['date'])

            self.input_amount = tk.Entry(edit_window)
            self.input_amount.grid(row=1, column=1, padx=5, pady=5)
            self.input_amount.insert(0, env['amount'])

            self.input_details = tk.Text(edit_window, height=5, width=40)
            self.input_details.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
            self.input_details.insert("1.0", env['details'])

            def close():
                edit_window.destroy()

            def apply():
                # todo - use input boxes instead, still need env[ID]
                editRow(connection(), str(env['table']), str(env['id']), str(env['date']), str(env['details']), str(env['amount']))

            tk.Button(edit_window, text='Apply', command=lambda: apply()).grid(row=2, column=2, padx=5, pady=5)
            tk.Button(edit_window, text='Cancel', command=lambda: close()).grid(row=3, column=2, padx=5, pady=5)

        else:
            print('Please select a row to edit')

    def editExpensePopup(self):
        if env['table'] == 'Expenses':
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Entry")
            edit_window.geometry('400x200')

            # Populate entries with selected item details
            tk.Label(edit_window, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Amount").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Details").grid(row=0, column=2, sticky="w", padx=5, pady=5)

            self.input_date = tk.Entry(edit_window)
            self.input_date.grid(row=0, column=1, padx=5, pady=5)
            self.input_date.insert(0, env['date'])

            self.input_amount = tk.Entry(edit_window)
            self.input_amount.grid(row=1, column=1, padx=5, pady=5)
            self.input_amount.insert(0, env['amount'])

            self.input_details = tk.Text(edit_window, height=5, width=40)
            self.input_details.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
            self.input_details.insert("1.0", env['details'])
        else:
            print('Please select a row to edit')

    def selectItem(self, event, table_name):
        table_widget = event.widget
        selected_item = table_widget.selection()

        if selected_item:

            item_id = selected_item[0]
            item_values = table_widget.item(item_id, 'values')

            # Assign the values from item_values to the selected attributes
            env['table'] = table_name
            env['id'] = item_values[0]
            env['date'] = item_values[1]
            env['details'] = item_values[2]
            env['amount'] = item_values[3]

            print('env table: ' + env['table'])
            print('env id: ' + env['id'])
            print('env date: ' + env['date'])
            print('env details: ' + env['details'])
            print('env amount: ' + env['amount'])
        else:
            env['table'] = None
            env['id'] = None
            env['date'] = None
            env['details'] = None
            env['amount'] = None

            print('env table: ' + env['table'])
            print('env id: ' + env['id'])
            print('env date: ' + env['date'])
            print('env details: ' + env['details'])
            print('env amount: ' + env['amount'])

    def addPopup(self, table):
        pass

    def deletePopup(self, table):
        print("are you sure you want to delete this row?")
        pass


class MainGUI_backup:
    def __init__(self, root):
        self.root = root
        self.root.focus_force()
        self.root.title("Student Loan CRUD App")  # Window name
        self.root.geometry('470x650')
        self.root.resizable(width=False, height=False)

        # Title frame
        self.title_frame = tk.Frame(self.root)
        self.title_frame.pack(anchor='n')
        tk.Label(self.title_frame, text='Tracking Student Loan Income & Expenses\n', font=('Inter', 18, 'bold')).pack(expand=False)

        # Content frame         width=405
        self.content_frame = tk.Frame(self.root, padx=20)
        self.content_frame.pack(expand=True, fill='both')

        # self.table = None
        self.income_table = None
        self.expense_table = None
        self.input_date = None
        self.input_total = None
        self.input_amount = None
        self.input_details = None
        self.btnFrame = None

        # Temp
        self.selectedTable = None
        self.selectedID = None
        self.selectedDate = None
        self.selectedDetails = None
        self.selectedAmount = None

        env['table'] = str(self.selectedTable)
        env['id'] = str(self.selectedID)
        env['date'] = str(self.selectedDate)
        env['details'] = str(self.selectedDetails)
        env['amount'] = str(self.selectedAmount)

        # Display table windows
        self.incomeTable()
        self.summaryPanel()
        self.expensesTable()

    def summaryPanel(self):
        # MySQL queries
        conn = connection()
        total_income = incomeTotal(conn)
        total_spent = expenseTotal(conn)
        unspent = float(total_income - total_spent)
        percentage = round((float(float(unspent) / float(total_income)) * 100), 2)

        # Shift row - 1 to remove blank row above this row
        tk.Label(self.content_frame, text=f'Total Loaned:     $ {total_income}').grid(row=1, column=1)
        tk.Label(self.content_frame, text=f'Total Spent:     $ {total_spent}').grid(row=2, column=1)
        tk.Label(self.content_frame, text=f'Total Unspent:    $ {unspent}').grid(row=1, column=2)
        tk.Label(self.content_frame, text=f'                         % {percentage}').grid(row=2, column=2)

    def incomeTable(self):
        tk.Label(self.content_frame, text='\nIncome', font=('Inter', 16, 'bold')).grid(row=3, column=1)
        self.income_table = ttk.Treeview(self.content_frame, show='headings', columns=('ID', 'Date', 'Details', 'Amount'), height=5)
        self.income_table.heading('Date', text='Date')
        self.income_table.heading('Amount', text='Amount')
        self.income_table.heading('Details', text='Details')

        self.income_table.column('ID', width=10)
        self.income_table.column('Date', width=90)
        self.income_table.column('Details', width=250)
        self.income_table.column('Amount', width=80)

        if connection() is not None:
            data = selectIncome(connection())
            for row in data:
                self.income_table.insert("", tk.END, values=row)
            connection().close()

        self.income_table.grid(row=4, column=1, columnspan=5)
        self.income_table.bind('<ButtonRelease-1>', lambda event: self.selectItem(event, 'Income'))

        # Buttons
        self.btnFrame = ttk.Frame(self.content_frame)
        self.btnFrame.grid(row=5, column=1, columnspan=4)
        tk.Button(self.btnFrame, text="Add Row", command=lambda: self.addPopup('Income')).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Edit Row", command=lambda: self.editIncomePopup()).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Delete Row", command=lambda: self.deletePopup('Income')).pack(side=tk.LEFT, padx=5, pady=5)

    def expensesTable(self):
        tk.Label(self.content_frame, text='\n\n\nExpenses', font=('Inter', 16, 'bold')).grid(row=6, column=1)

        # Define the table
        self.expense_table = ttk.Treeview(self.content_frame, show='headings', columns=('ID', 'Date', 'Details', 'Amount'))
        self.expense_table.heading('Date', text='Date')
        self.expense_table.heading('Amount', text='Amount')
        self.expense_table.heading('Details', text='Details')
        self.expense_table.column('ID', width=10)
        self.expense_table.column('Date', width=90)
        self.expense_table.column('Details', width=250)
        self.expense_table.column('Amount', width=80)

        # Fill the table w/ data
        if connection() is not None:
            data = selectExpenses(connection())
            for row in data:
                self.expense_table.insert("", tk.END, values=row)
            connection().close()

        self.expense_table.grid(row=7, column=1, columnspan=4)
        self.expense_table.bind('<ButtonRelease-1>', lambda event: self.selectItem(event, 'Expenses'))

        # Interaction buttons
        self.btnFrame = ttk.Frame(self.content_frame)
        self.btnFrame.grid(row=8, column=1, columnspan=4)
        tk.Button(self.btnFrame, text="Add Row", command=lambda: self.addPopup('Expenses')).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Edit Row", command=lambda: self.editExpensePopup()).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.btnFrame, text="Delete Row", command=lambda: self.deletePopup('Expenses')).pack(side=tk.LEFT, padx=5, pady=5)

    def editIncomePopup(self):
        if env['table'] == 'Income':
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Entry")
            edit_window.geometry('625x175')

            # Populate entries with selected item details
            tk.Label(edit_window, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Amount").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Details").grid(row=0, column=2, sticky="w", padx=5, pady=5)

            self.input_date = tk.Entry(edit_window)
            self.input_date.grid(row=0, column=1, padx=5, pady=5)
            self.input_date.insert(0, env['date'])

            self.input_amount = tk.Entry(edit_window)
            self.input_amount.grid(row=1, column=1, padx=5, pady=5)
            self.input_amount.insert(0, env['amount'])

            self.input_details = tk.Text(edit_window, height=5, width=40)
            self.input_details.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
            self.input_details.insert("1.0", env['details'])

            def close():
                edit_window.destroy()

            def apply():
                # todo - use input boxes instead, still need env[ID]
                editRow(connection(), str(env['table']), str(env['id']), str(env['date']), str(env['details']), str(env['amount']))

            tk.Button(edit_window, text='Apply', command=lambda: apply()).grid(row=2, column=2, padx=5, pady=5)
            tk.Button(edit_window, text='Cancel', command=lambda: close()).grid(row=3, column=2, padx=5, pady=5)

        else:
            print('Please select a row to edit')

    def editExpensePopup(self):
        if env['table'] == 'Expenses':
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Entry")
            edit_window.geometry('400x200')

            # Populate entries with selected item details
            tk.Label(edit_window, text="Date").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Amount").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            tk.Label(edit_window, text="Details").grid(row=0, column=2, sticky="w", padx=5, pady=5)

            self.input_date = tk.Entry(edit_window)
            self.input_date.grid(row=0, column=1, padx=5, pady=5)
            self.input_date.insert(0, env['date'])

            self.input_amount = tk.Entry(edit_window)
            self.input_amount.grid(row=1, column=1, padx=5, pady=5)
            self.input_amount.insert(0, env['amount'])

            self.input_details = tk.Text(edit_window, height=5, width=40)
            self.input_details.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
            self.input_details.insert("1.0", env['details'])
        else:
            print('Please select a row to edit')

    def selectItem(self, event, table_name):
        table_widget = event.widget
        selected_item = table_widget.selection()

        if selected_item:

            item_id = selected_item[0]
            item_values = table_widget.item(item_id, 'values')

            # Assign the values from item_values to the selected attributes
            env['table'] = table_name
            env['id'] = item_values[0]
            env['date'] = item_values[1]
            env['details'] = item_values[2]
            env['amount'] = item_values[3]

            print('env table: ' + env['table'])
            print('env id: ' + env['id'])
            print('env date: ' + env['date'])
            print('env details: ' + env['details'])
            print('env amount: ' + env['amount'])
        else:
            env['table'] = None
            env['id'] = None
            env['date'] = None
            env['details'] = None
            env['amount'] = None

            print('env table: ' + env['table'])
            print('env id: ' + env['id'])
            print('env date: ' + env['date'])
            print('env details: ' + env['details'])
            print('env amount: ' + env['amount'])

    def addPopup(self, table):
        pass

    def deletePopup(self, table):
        print("are you sure you want to delete this row?")
        pass


if __name__ == '__main__':
    root = tk.Tk()
    app = MainGUI(root)
    # app = MainGUI_backup(root)

    root.mainloop()
