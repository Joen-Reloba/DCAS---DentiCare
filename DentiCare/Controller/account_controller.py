from PyQt6.QtWidgets import QMessageBox, QHeaderView, QTableWidgetItem
from DentiCare.Model.account_model import AccountModel
from DentiCare.Model.staff_model import StaffModel


class AccountTabController:
    """
    Account Controller - Orchestrates between View and Model.
    Handles all business logic, validation, and data processing.
    """

    def __init__(self, view):
        self.view = view
        self.staff_model = StaffModel()
        self.account_model = AccountModel()
        self.current_form = None  # Track current dialog

    def _formatDateTime(self, datetime_obj):
        """Format datetime to 12-hour format with AM/PM"""
        if not datetime_obj:
            return 'N/A'

        return datetime_obj.strftime('%Y-%m-%d %I:%M %p')

    def switchToAccountTab(self):
       #swicth to account tab
        self.view.switchToTab(2)
        self.loadAccountTable()


    def showAddForm(self):
       #pop up the add account form
        # View creates the dialog
        self.current_form = self.view.createDialog("DentiCare/ui/accountAddForm.ui")

        # Connect the search button
        self.current_form.searchIconBtn.clicked.connect(self.searchAndValidateStaff)

        # Connect the add button
        self.current_form.accountFormAddBtn.clicked.connect(self.addAccount)

        # Show the form
        self.current_form.exec()

    def searchAndValidateStaff(self):
       #search for the ID and check if role is authorized
        form = self.current_form

        try:
            # Get staff ID from form
            staff_id = form.account_staffIDField.text().strip()

            # Validate input
            if not staff_id:
                QMessageBox.warning(form, "Input Error", "Please enter a Staff ID")
                return

            # Get staff data from Model
            staff_data = self.staff_model.getStaffByID(staff_id)

            if staff_data is None:
                QMessageBox.warning(form, "Not Found", "Staff ID not found in database")
                form.account_staffnameField.setText("")
                return

            #  Check if role is valid for account creation
            role = staff_data['Role']
            if role.lower() not in ['admin', 'frontdesk']:
                QMessageBox.warning(
                    form,
                    "Invalid Role",
                    f"Cannot create account for role '{role}'.\n"
                    f"Only Admin and Front Desk staff can have accounts."
                )
                form.account_staffnameField.setText("")
                return

            # Check if account already exists
            if self.account_model.accountExists(staff_id):
                QMessageBox.warning(
                    form,
                    "Account Exists",
                    f"An account already exists for this Staff ID ({staff_id})"
                )
                return

            # Format and display the name
            full_name = self._formatFullName(staff_data)
            form.account_staffnameField.setText(full_name)

            QMessageBox.information(
                form,
                "Valid Staff",
                f"Staff found!\nName: {full_name}\nRole: {role}\n\n"
                f"You can now create an account."
            )

        except Exception as e:
            QMessageBox.critical(form, "Error", f"Error searching for staff: {str(e)}")

    def addAccount(self):
        #add new account for staff member
        form = self.current_form

        try:
            # Extract data from form
            staff_id = form.account_staffIDField.text().strip()
            username = form.account_usernameField.text().strip()
            password = form.account_passwordField.text().strip()

            # Validate required fields
            if not staff_id:
                QMessageBox.warning(form, "Input Error",
                                    "Please search for a Staff ID first")
                return

            if not username:
                QMessageBox.warning(form, "Input Error",
                                    "Please enter a username")
                return

            if not password:
                QMessageBox.warning(form, "Input Error",
                                    "Please enter a password")
                return

            # Verify staff exists and has valid role
            staff_data = self.staff_model.getStaffByID(staff_id)

            if staff_data is None:
                QMessageBox.warning(form, "Error",
                                    "Staff ID not found. Please search again.")
                return

            role = staff_data['Role']

            #  checks only admin and frontdesk can have accounts
            if role.lower() not in ['admin', 'frontdesk']:
                QMessageBox.warning(
                    form,
                    "Invalid Role",
                    f"Cannot create account for role '{role}'"
                )
                return

            # Check if username already exists
            if self.account_model.usernameExists(username):
                QMessageBox.warning(
                    form,
                    "Username Exists",
                    f"Username '{username}' is already taken. Please choose another."
                )
                return

            # Double-check if account exists
            if self.account_model.accountExists(staff_id):
                QMessageBox.warning(
                    form,
                    "Account Exists",
                    "An account already exists for this Staff ID"
                )
                return

            # Add account via Model
            self.account_model.add_account(staff_id, username, password)

            QMessageBox.information(
                form,
                "Success",
                "Account created successfully!"
            )

            # Refresh table and close form
            self.loadAccountTable()
            form.close()

        except Exception as e:
            QMessageBox.critical(form, "Database Error",
                                 f"Error adding account: {str(e)}")

    # ========== UPDATE ACCOUNT ==========

    def showUpdateForm(self):
        #pops up the update form for account
        staff_id = self._getSelectedStaffID() #call function to get ID
        if not staff_id:
            return

        try:
            # Get data from Model
            account_data = self.account_model.getAccountByStaffID(staff_id)

            if not account_data:
                QMessageBox.warning(self.view, "Error", "Account data not found")
                return

            # Create form
            self.current_form = self.view.createDialog("DentiCare/ui/accountUpdateForm.ui")

            # Verify required widgets exist for  debugging lng
            required_widgets = [
                'account_staffnameField',
                'account_usernameField',
                'account_passwordField',
                'accountFormUpdateBtn'
            ]

            missing_widgets = []
            for widget_name in required_widgets:
                if not hasattr(self.current_form, widget_name):
                    missing_widgets.append(widget_name)

            if missing_widgets:
                QMessageBox.critical(self.view, "UI Error",
                                     f"Missing widgets: {', '.join(missing_widgets)}")
                return

            # Populate form with existing data
            full_name = self._formatFullName(account_data)
            self.current_form.account_staffnameField.setText(full_name)
            self.current_form.account_usernameField.setText(account_data['Username'])
            self.current_form.account_passwordField.setText(account_data['Password'])

            # Connect update button
            self.current_form.accountFormUpdateBtn.clicked.connect(
                lambda: self.updateAccount(staff_id)
            )

            # Show form
            self.current_form.exec()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self.view, "Error",
                                 f"Error opening update form: {str(e)}\n\n"
                                 f"Details:\n{error_details}")

    def updateAccount(self, staff_id):
        #for updating acc info
        form = self.current_form

        # Extract data from view
        username = form.account_usernameField.text().strip()
        password = form.account_passwordField.text().strip()

        # Validate if empty
        if not username or not password:
            QMessageBox.warning(form, "Input Error",
                                "Please fill in all required fields")
            return

        try:
            # Update via Model
            self.account_model.updateAccount(staff_id, username, password)

            QMessageBox.information(self.view, "Success",
                                    "Account updated successfully")
            self.loadAccountTable()
            form.close()

        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error updating account: {str(e)}")


    def deleteAccount(self):
       #delete account
        staff_id = self._getSelectedStaffID()
        if not staff_id:
            return

        try:
            # Get account data for confirmation
            account_data = self.account_model.getAccountByStaffID(staff_id)

            if not account_data:
                QMessageBox.warning(self.view, "Error", "Account data not found")
                return

            # Confirmation dialog
            account_owner = self._formatFullName(account_data)
            reply = QMessageBox.question(
                self.view,
                'Confirm Delete',
                f"Are you sure you want to delete this account?\n\n"
                f"Staff ID: {staff_id}\n"
                f"Account Owner: {account_owner}\n"
                f"Username: {account_data['Username']}\n\n"
                f"This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Delete via Model
                self.account_model.deleteAccount(staff_id)

                QMessageBox.information(self.view, "Success",
                                        f"Account '{account_data['Username']}' deleted successfully")
                self.loadAccountTable()

        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error deleting account: {str(e)}")



    def loadAccountTable(self):
        #load table with data
        try:
            # Get data from Model
            account_list = self.account_model.getAllAccounts()

            # Get table widget from View
            table = self.view.getAccountTable()

            # Configure table headers
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # StaffID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Full Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Username
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Password
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Role
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch) # Added At
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)# Updated At

            # Populate table
            table.setRowCount(len(account_list))

            for row, account in enumerate(account_list):
                # Format data for display
                full_name = self._formatFullName(account)

                # Set table items
                table.setItem(row, 0, QTableWidgetItem(str(account['StaffID'])))
                table.setItem(row, 1, QTableWidgetItem(full_name))
                table.setItem(row, 2, QTableWidgetItem(account['Username']))
                table.setItem(row, 3, QTableWidgetItem(account['Password']))
                table.setItem(row, 4, QTableWidgetItem(account['Role']))

                created_at_str = self._formatDateTime(account.get('created_at'))
                updated_at_str = self._formatDateTime(account.get('updated_at'))

                table.setItem(row, 5, QTableWidgetItem(created_at_str))
                table.setItem(row, 6, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Load Error",
                                 f"Error loading account table: {str(e)}")



    def _getSelectedStaffID(self):
        #get selected staff by selected row
        table = self.view.getAccountTable()
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.view, "Selection Error",
                                "Please select an account from the table first")
            return None

        staff_id = table.item(row, 0).text() #get id by selected row 1st column
        return staff_id

    def _formatFullName(self, data):
        """Format full name for display"""
        middle = data.get('StaffMname') or ''
        return f"{data['StaffLname']}, {data['StaffFname']} {middle}".strip()