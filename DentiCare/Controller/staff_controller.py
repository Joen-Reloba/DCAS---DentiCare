
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from DentiCare.Model.staff_model import StaffModel


class StaffTabController:
    """Staff Controller - Orchestrates between View and Model."""

    def __init__(self, view):
        self.view = view
        self.model = StaffModel()
        self.current_form = None

    def _formatDateTime(self, datetime_obj):
        """Format datetime to 12-hour format with AM/PM"""
        if not datetime_obj:
            return 'N/A'
        return datetime_obj.strftime('%Y-%m-%d %I:%M %p')

    def switchToStaffTab(self):
        """Switch to staff tab then load data"""
        self.view.switchToTab(1)
        self.loadStaffTable()

    def showAddForm(self):
        """Show add form dialog"""
        self.current_form = self.view.createDialog("DentiCare/ui/staffAddForm.ui")
        self._setupFormBehavior(self.current_form)
        self.current_form.staffFormAddBtn.clicked.connect(self.addStaff)
        self.current_form.exec()

    def _setupFormBehavior(self, form):
        """Setup form behavior (business rules)"""

        def onRoleChange(role):
            if role.lower() == "dentist":
                form.licenseField.setEnabled(True)
            else:
                form.licenseField.setEnabled(False)
                form.licenseField.setText("")

        form.roleField.currentTextChanged.connect(onRoleChange)
        onRoleChange(form.roleField.currentText())

    def addStaff(self):
        """Add new staff member - created_at is set automatically"""
        form = self.current_form

        # Extract data from form
        fn = form.fnameField.text().strip()
        mn = form.mnameField.text().strip()
        ln = form.lnameField.text().strip()
        sex = form.sexField.currentText()
        bday = form.bdayField.date().toString('yyyy-MM-dd')
        contact = form.contactField.text().strip()
        barangay = form.barangayField.text().strip()
        city = form.cityField.text().strip()
        province = form.provinceField.text().strip()
        zipcode = form.zipcodeField.text().strip()
        role = form.roleField.currentText()
        datehired = form.dateHiredField.date().toString('yyyy-MM-dd')

        # Validate required fields
        if not fn or not ln or not sex or not contact or not city or not role:
            QMessageBox.warning(form, "Input Error",
                                "Please fill in all required fields:\n"
                                "First Name, Last Name, Sex, Contact, City, Role")
            return

        # Handle license for dentists
        licenseNum = None
        if role.lower() == "dentist":
            licenseNum = form.licenseField.text().strip()
            if not licenseNum:
                QMessageBox.warning(form, "Input Error",
                                    "License number is required for Dentist role")
                return

        try:
            # Call Model to save data (created_at set automatically by MySQL)
            new_staff_id = self.model.addStaff(
                fn, mn, ln, sex, bday, contact,
                barangay, city, province, zipcode,
                role, datehired, licenseNum
            )

            # Success feedback
            QMessageBox.information(form, "Success",
                                    f"Staff added successfully with ID: {new_staff_id}")

            # Refresh the table and close form
            self.loadStaffTable()
            form.close()

        except Exception as e:
            QMessageBox.critical(form, "Database Error",
                                 f"Error adding staff: {str(e)}")

    def showUpdateForm(self):
        """Show update form with selected staff data"""
        staff_id = self._getSelectedStaffID()
        if not staff_id:
            return

        try:
            staff_data = self.model.getStaffByID(staff_id)

            if not staff_data:
                QMessageBox.warning(self.view, "Error", "Staff data not found")
                return

            # Create form
            self.current_form = self.view.createDialog("DentiCare/ui/staffUpdateForm.ui")
            self._setupFormBehavior(self.current_form)

            # Populate form with existing data
            self._populateUpdateForm(self.current_form, staff_data)

            # Connect update button
            self.current_form.staffFormUpdateBtn.clicked.connect(
                lambda: self.updateStaff(staff_id)
            )

            self.current_form.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Error opening update form: {str(e)}")

    def _populateUpdateForm(self, form, staff_data):
        """Populate form with selected staff data"""
        form.staffIDField.setText(str(staff_data['StaffID']))
        form.fnameField.setText(staff_data['StaffFname'])
        form.mnameField.setText(staff_data['StaffMname'] or "")
        form.lnameField.setText(staff_data['StaffLname'])
        form.sexField.setCurrentText(staff_data['Sex'])

        # Handle date fields safely
        birthday = staff_data['Birthday']
        if birthday:
            form.bdayField.setDate(QDate(birthday.year, birthday.month, birthday.day))

        form.contactField.setText(staff_data['ContactNumber'])
        form.barangayField.setText(staff_data['Barangay'] or "")
        form.cityField.setText(staff_data['City'])
        form.provinceField.setText(staff_data['Province'] or "")
        form.zipcodeField.setText(str(staff_data['Zipcode'] or ""))
        form.roleField.setCurrentText(staff_data['Role'])

        date_hired = staff_data['DateHired']
        if date_hired:
            form.dateHiredField.setDate(QDate(date_hired.year, date_hired.month, date_hired.day))

        form.licenseField.setText(staff_data.get('LicenseNum') or "")

    def updateStaff(self, staff_id):
        """Update staff info - updated_at is set automatically"""
        form = self.current_form

        # Extract data
        fn = form.fnameField.text().strip()
        mn = form.mnameField.text().strip()
        ln = form.lnameField.text().strip()
        sex = form.sexField.currentText()
        bday = form.bdayField.date().toString('yyyy-MM-dd')
        contact = form.contactField.text().strip()
        barangay = form.barangayField.text().strip()
        city = form.cityField.text().strip()
        province = form.provinceField.text().strip()
        zipcode = form.zipcodeField.text().strip()
        role = form.roleField.currentText()
        datehired = form.dateHiredField.date().toString('yyyy-MM-dd')
        licenseNum = form.licenseField.text().strip() if role.lower() == "dentist" else None

        # Validate
        if not fn or not ln or not sex or not contact or not city or not role:
            QMessageBox.warning(form, "Input Error",
                                "Please fill in all required fields")
            return

        try:
            # Update via Model (updated_at automatically set by MySQL)
            self.model.updateStaff(
                staff_id, fn, mn, ln, sex, bday, contact,
                barangay, city, province, zipcode,
                role, datehired, licenseNum
            )

            QMessageBox.information(self.view, "Success",
                                    "Staff updated successfully")
            self.loadStaffTable()
            form.close()

        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error updating staff: {str(e)}")

    def deleteStaff(self):
        """Delete selected staff member"""
        staff_id = self._getSelectedStaffID()
        if not staff_id:
            return

        try:
            staff_data = self.model.getStaffByID(staff_id)

            if not staff_data:
                QMessageBox.warning(self.view, "Error", "Staff data not found")
                return

            # Confirmation dialog
            staff_name = f"{staff_data['StaffFname']} {staff_data['StaffLname']}"
            reply = QMessageBox.question(
                self.view,
                'Confirm Delete',
                f"Are you sure you want to delete this staff member?\n\n"
                f"Staff ID: {staff_id}\n"
                f"Name: {staff_name}\n"
                f"Role: {staff_data['Role']}\n\n"
                f"This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.model.deleteStaff(staff_id)

                QMessageBox.information(self.view, "Success",
                                        f"Staff member {staff_name} deleted successfully")
                self.loadStaffTable()

        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error deleting staff: {str(e)}")

    def loadStaffTable(self):
        """Load staff table with timestamps in 12-hour format"""
        try:
            # Get data from Model (includes created_at and updated_at)
            staff_list = self.model.getAllStaff()

            # Get table widget from View
            table = self.view.getStaffTable()

            # Configure table headers (now includes 2 timestamp columns)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Sex
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Birthday
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Contact
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Address
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Role
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Date Hired
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # License
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Added At
            header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)  # Updated At

            # Populate table
            table.setRowCount(len(staff_list))

            for row, staff in enumerate(staff_list):
                # Format data for display
                full_name = self._formatFullName(staff)
                address = self._formatAddress(staff)
                birthday_str = self._formatDate(staff['Birthday'])
                date_hired_str = self._formatDate(staff['DateHired'])
                license_num = staff['LicenseNum'] or 'N/A'

                # ✅ Format timestamps in 12-hour format
                created_at_str = self._formatDateTime(staff.get('created_at'))
                updated_at_str = self._formatDateTime(staff.get('updated_at'))

                # Set table items
                table.setItem(row, 0, QTableWidgetItem(str(staff['StaffID'])))
                table.setItem(row, 1, QTableWidgetItem(full_name))
                table.setItem(row, 2, QTableWidgetItem(staff['Sex']))
                table.setItem(row, 3, QTableWidgetItem(birthday_str))
                table.setItem(row, 4, QTableWidgetItem(staff['ContactNumber']))
                table.setItem(row, 5, QTableWidgetItem(address))
                table.setItem(row, 6, QTableWidgetItem(staff['Role']))
                table.setItem(row, 7, QTableWidgetItem(date_hired_str))
                table.setItem(row, 8, QTableWidgetItem(license_num))

                # ✅ Add timestamp columns
                table.setItem(row, 9, QTableWidgetItem(created_at_str))
                table.setItem(row, 10, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Load Error",
                                 f"Error loading staff table: {str(e)}")

    def _getSelectedStaffID(self):
        """Get the selected staff ID from table"""
        table = self.view.getStaffTable()
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.view, "Selection Error",
                                "Please select a staff member from the table first")
            return None

        staff_id = table.item(row, 0).text()
        return staff_id

    def _formatFullName(self, staff):
        """Format full name for display"""
        middle = staff['StaffMname'] or ''
        return f"{staff['StaffLname']}, {staff['StaffFname']} {middle}".strip()

    def _formatAddress(self, staff):
        """Format address for display"""
        zipcode = staff['Zipcode'] or ''
        return f"{staff['Barangay']}, {staff['City']}, {staff['Province']}, {zipcode}".strip()

    def _formatDate(self, date_obj):
        """Format date object to string"""
        return date_obj.strftime('%Y-%m-%d') if date_obj else ''


# ============================================================================
# 2. UPDATED service_controller.py - With Timestamp Columns
# ============================================================================

from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QDialog
from PyQt6.uic import loadUi
from DentiCare.Model.service_model import ServiceModel


class ServiceTabController:
    def __init__(self, view):
        self.view = view
        self.service_model = ServiceModel()
        self.updateForm = None
        self.addForm = None

    def _formatDateTime(self, datetime_obj):
        """Format datetime to 12-hour format with AM/PM"""
        if not datetime_obj:
            return 'N/A'
        return datetime_obj.strftime('%Y-%m-%d %I:%M %p')

    def switchToServiceTab(self):
        """Switch to service tab"""
        self.view.switchToTab(3)
        self.loadServiceTable()

    def showServiceAddForm(self):
        self.addForm = QDialog(self.view)
        loadUi("serviceAddForm.ui", self.addForm)
        self.addForm.serviceFormAddBtn.clicked.connect(self.addService)
        self.addForm.exec()

    def getServiceInfo(self):
        return (
            self.addForm.serviceNameField.text(),
            self.addForm.servicePriceField.text()
        )

    def addService(self):
        serviceInfo = self.getServiceInfo()

        if serviceInfo[0].strip() == "" or serviceInfo[1].strip() == "":
            QMessageBox.warning(self.addForm, "Input Error", "Please fill in all required fields")
            return

        try:
            self.service_model.add_service(*serviceInfo)
            QMessageBox.information(self.addForm, "Success", "Service added successfully")
            self.addForm.close()
            self.loadServiceTable()
        except Exception as e:
            QMessageBox.critical(self.addForm, "Database Error", f"Error adding Service: {e}")

    def loadServiceTable(self):
        """Load service table with timestamps in 12-hour format"""
        try:
            serviceList = self.service_model.getAllService()
            table = self.view.servicesTable
            header = table.horizontalHeader()

            # Configure headers (now includes 2 timestamp columns)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Price
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Added At
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Updated At

            table.setRowCount(len(serviceList))

            for row, svc in enumerate(serviceList):
                # ✅ Format timestamps in 12-hour format
                created_at_str = self._formatDateTime(svc.get('created_at'))
                updated_at_str = self._formatDateTime(svc.get('updated_at'))

                table.setItem(row, 0, QTableWidgetItem(str(svc["ServiceID"])))
                table.setItem(row, 1, QTableWidgetItem(svc["ServiceName"]))
                table.setItem(row, 2, QTableWidgetItem(f"{float(svc['Price']):.2f}"))

                # ✅ Add timestamp columns
                table.setItem(row, 3, QTableWidgetItem(created_at_str))
                table.setItem(row, 4, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load services: {e}")

    def getSelectedService(self):
        row = self.view.servicesTable.currentRow()
        if row < 0:
            QMessageBox.warning(self.view, "Selection Error", "Please select a service first.")
            return None
        return self.view.servicesTable.item(row, 0).text()

    def showServiceUpdateForm(self):
        serviceID = self.getSelectedService()
        if not serviceID:
            return

        try:
            data = self.service_model.getServiceByID(serviceID)
            if not data:
                QMessageBox.warning(self.view, "Error", "Service not found.")
                return

            self.updateForm = QDialog(self.view)
            loadUi("serviceUpdateForm.ui", self.updateForm)

            self.updateForm.serviceIDField.setText(serviceID)
            self.updateForm.serviceNameField.setText(data["ServiceName"])
            self.updateForm.servicePriceField.setText(str(data["Price"]))

            self.updateForm.serviceFormUpdateBtn.clicked.connect(
                lambda: self.updateService(serviceID)
            )

            self.updateForm.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error opening update form: {e}")

    def updateService(self, serviceID):
        name = self.updateForm.serviceNameField.text().strip()
        price = self.updateForm.servicePriceField.text().strip()

        if name == "" or price == "":
            QMessageBox.warning(self.updateForm, "Input Error", "Please fill in all required fields")
            return

        try:
            self.service_model.updateService(serviceID, name, price)
            QMessageBox.information(self.view, "Success", "Service updated successfully")
            self.updateForm.close()
            self.loadServiceTable()

        except Exception as e:
            QMessageBox.critical(self.updateForm, "Database Error", f"Error updating service: {e}")

    def deleteService(self):
        serviceID = self.getSelectedService()
        if not serviceID:
            return

        data = self.service_model.getServiceByID(serviceID)
        if not data:
            QMessageBox.warning(self.view, "Error", "Service not found.")
            return

        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            f"Delete Service {data['ServiceName']} (ID: {serviceID})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.service_model.deleteService(serviceID)
                QMessageBox.information(self.view, "Success", "Service deleted.")
                self.loadServiceTable()
            except Exception as e:
                QMessageBox.critical(self.view, "Database Error", f"Error deleting service: {e}")


# ============================================================================
# 3. UPDATED patient_controller.py - With Timestamp Columns
# ============================================================================

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QDialog
from PyQt6.uic import loadUi
from DentiCare.Model.patient_model import PatientModel


class PatientTabController:
    """CONTROLLER - Handles business logic and coordinates between View and Model"""

    def __init__(self, view):
        self.view = view
        self.patient_model = PatientModel()
        self.current_form = None

    def _formatDateTime(self, datetime_obj):
        """Format datetime to 12-hour format with AM/PM"""
        if not datetime_obj:
            return 'N/A'
        return datetime_obj.strftime('%Y-%m-%d %I:%M %p')

    def showPatientAddForm(self):
        """Show the add patient form"""
        try:
            self.current_form = QDialog(self.view)
            loadUi("patientAddForm.ui", self.current_form)
            self.current_form.patientFormAddBtn.clicked.connect(self.addPatient)
            self.current_form.exec()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load form: {e}")

    def addPatient(self):
        """Add a new patient"""
        patientInfo = self._getPatientInfoFromForm(self.current_form)

        if not self._validatePatientData(patientInfo):
            QMessageBox.warning(self.current_form, "Input Error",
                                "Please fill in all required fields (First Name, Last Name, Sex, Birthday, Contact)")
            return

        try:
            self.patient_model.add_patient(*patientInfo)
            QMessageBox.information(self.current_form, "Success", "Patient added successfully")
            self.current_form.close()
            self.loadPatientTable()

        except Exception as e:
            QMessageBox.critical(self.current_form, "Database Error",
                                 f"Error adding patient: {e}")

    def loadPatientTable(self):
        """Load patient data into table with timestamps in 12-hour format"""
        try:
            patientList = self.patient_model.getAllPatient()

            table = self.view.patientTable
            header = table.horizontalHeader()

            # Set column resize modes (now includes 2 timestamp columns)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # PatientID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Patient FullName
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Sex
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Birthday
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # ContactNum
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Added At
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Updated At

            table.setRowCount(len(patientList))

            # Populate table
            for row, patient in enumerate(patientList):
                fullName = f"{patient['PatientLname']}, {patient['PatientFname']} {patient['PatientMname'] or ''}".strip()
                birthday_str = patient['Birthday'].strftime('%Y-%m-%d') if patient['Birthday'] else ''

                # ✅ Format timestamps in 12-hour format
                created_at_str = self._formatDateTime(patient.get('created_at'))
                updated_at_str = self._formatDateTime(patient.get('updated_at'))

                table.setItem(row, 0, QTableWidgetItem(str(patient['PatientID'])))
                table.setItem(row, 1, QTableWidgetItem(fullName))
                table.setItem(row, 2, QTableWidgetItem(patient['Sex']))
                table.setItem(row, 3, QTableWidgetItem(birthday_str))
                table.setItem(row, 4, QTableWidgetItem(patient['ContactNumber']))

                # ✅ Add timestamp columns
                table.setItem(row, 5, QTableWidgetItem(created_at_str))
                table.setItem(row, 6, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load patients: {e}")

    def getSelectedPatient(self):
        """Get the selected patient ID from table"""
        table = self.view.patientTable
        row = table.currentRow()

        if row < 0:
            QMessageBox.warning(self.view, "Selection Error",
                                "Please select a patient from the table first.")
            return None

        patientID = table.item(row, 0).text()
        return patientID

    def showPatientUpdateForm(self):
        """Show the update patient form"""
        patientID = self.getSelectedPatient()
        if not patientID:
            return

        try:
            patientData = self.patient_model.getPatientByID(patientID)

            if not patientData:
                QMessageBox.warning(self.view, "Error", "Patient data not found")
                return

            self.current_form = QDialog(self.view)

            try:
                loadUi("patientUpdateForm.ui", self.current_form)
            except Exception as e:
                QMessageBox.critical(self.view, "UI Load Error",
                                     f"Failed to load patientUpdateForm.ui: {e}")
                return

            self._populateUpdateForm(patientData)

            self.current_form.patientFormUpdateBtn.clicked.connect(
                lambda: self.updatePatient(patientID))

            self.current_form.exec()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self.view, "Error",
                                 f"Error opening update form: {e}\n\n"
                                 f"Details:\n{error_details}")

    def updatePatient(self, patientID):
        """Update existing patient"""
        patientInfo = self._getPatientInfoFromForm(self.current_form)

        if not self._validatePatientData(patientInfo):
            QMessageBox.warning(self.current_form, "Input Error",
                                "Please fill in all required fields")
            return

        try:
            self.patient_model.updatePatient(patientID, *patientInfo)

            QMessageBox.information(self.view, "Success", "Patient updated successfully")
            self.loadPatientTable()
            self.current_form.close()

        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error updating patient: {e}")

    def deletePatient(self):
        """Delete the selected patient"""
        patientID = self.getSelectedPatient()
        if not patientID:
            return

        try:
            patientData = self.patient_model.getPatientByID(patientID)

            if not patientData:
                QMessageBox.warning(self.view, "Error", "Patient data not found")
                return

            fullName = f"{patientData['PatientLname']}, {patientData['PatientFname']} {patientData['PatientMname'] or ''}".strip()

            reply = QMessageBox.question(
                self.view,
                'Confirm Delete',
                f"Are you sure you want to delete this patient?\n\n"
                f"Patient ID: {patientID}\n"
                f"Name: {fullName}\n\n"
                f"This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.patient_model.deletePatient(patientID)

                QMessageBox.information(self.view, "Success",
                                        f"Patient {fullName} has been deleted successfully")

                self.loadPatientTable()

        except ValueError as ve:
            QMessageBox.warning(self.view, "Cannot Delete", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error deleting patient: {e}")

    def _getPatientInfoFromForm(self, form):
        """Extract patient information from form"""
        return (
            form.fnameField.text().strip(),
            form.mnameField.text().strip(),
            form.lnameField.text().strip(),
            form.sexField.currentText(),
            form.bdayField.date().toString('yyyy-MM-dd'),
            form.contactField.text().strip()
        )

    def _validatePatientData(self, patientInfo):
        """Validate patient data - all fields except middle name are required"""
        fname, mname, lname, sex, bday, contact = patientInfo
        required = [fname, lname, sex, bday, contact]
        return all(field for field in required)

    def _populateUpdateForm(self, patientData):
        """Populate update form with existing patient data"""
        self.current_form.patientIDField.setText(str(patientData['PatientID']))
        self.current_form.fnameField.setText(patientData['PatientFname'])
        self.current_form.mnameField.setText(patientData['PatientMname'] or '')
        self.current_form.lnameField.setText(patientData['PatientLname'])
        self.current_form.sexField.setCurrentText(patientData['Sex'])
        self.current_form.contactField.setText(patientData['ContactNumber'])

        birthday = patientData['Birthday']
        if birthday:
            self.current_form.bdayField.setDate(
                QDate(birthday.year, birthday.month, birthday.day))

    def searchPatientByName(self):
        """Search patients by name and update table"""
        search_name = self.view.patientnameSearchField.text().strip()