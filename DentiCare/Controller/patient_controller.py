from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QDialog
from PyQt6.uic import loadUi

from DentiCare.Model.patient_model import PatientModel


class PatientTabController:
    """CONTROLLER - Handles business logic and coordinates between View and Model"""

    def __init__(self, view):
        self.view = view  # this is the Staff view
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
            loadUi("DentiCare/ui/patientAddForm.ui", self.current_form)

            # Connect the add button
            self.current_form.patientFormAddBtn.clicked.connect(self.addPatient)

            self.current_form.exec()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load form: {e}")

    def addPatient(self):
        """Add a new patient"""
        # Get data from form
        patientInfo = self._getPatientInfoFromForm(self.current_form)

        # Validate
        if not self._validatePatientData(patientInfo):
            QMessageBox.warning(self.current_form, "Input Error",
                                "Please fill in all required fields (First Name, Last Name, Sex, Birthday, Contact)")
            return

        try:
            # Call model to add patient
            self.patient_model.add_patient(*patientInfo)

            QMessageBox.information(self.current_form, "Success", "Patient added successfully")
            self.current_form.close()
            self.loadPatientTable()

        except Exception as e:
            QMessageBox.critical(self.current_form, "Database Error",
                                 f"Error adding patient: {e}")

    def loadPatientTable(self):
        """Load patient data into the table"""
        try:
            patientList = self.patient_model.getAllPatient()

            table = self.view.patientTable
            header = table.horizontalHeader()

            # Set column resize modes
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # PatientID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Patient FullName
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Sex
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Birthday
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # ContactNum
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Added At
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Updated At

            table.setRowCount(len(patientList))

            # Populate table
            for row, patient in enumerate(patientList):
                fullName = f"{patient['PatientLname']}, {patient['PatientFname']} {patient['PatientMname'] or ''}".strip()
                birthday_str = patient['Birthday'].strftime('%Y-%m-%d') if patient['Birthday'] else ''

                table.setItem(row, 0, QTableWidgetItem(str(patient['PatientID'])))
                table.setItem(row, 1, QTableWidgetItem(fullName))
                table.setItem(row, 2, QTableWidgetItem(patient['Sex']))
                table.setItem(row, 3, QTableWidgetItem(birthday_str))
                table.setItem(row, 4, QTableWidgetItem(patient['ContactNumber']))

                created_at_str = self._formatDateTime(patient.get('created_at'))
                updated_at_str = self._formatDateTime(patient.get('updated_at'))

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

        patientID = table.item(row, 0).text()  # PatientID in first column
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

            # Create and load form
            self.current_form = QDialog(self.view)

            try:
                loadUi("DentiCare/ui/patientUpdateForm.ui", self.current_form)
            except Exception as e:
                QMessageBox.critical(self.view, "UI Load Error",
                                     f"Failed to load patientUpdateForm.ui: {e}")
                return

            # Populate form with existing data
            self._populateUpdateForm(patientData)

            # Connect update button
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
        # Get data from form
        patientInfo = self._getPatientInfoFromForm(self.current_form)

        # Validate
        if not self._validatePatientData(patientInfo):
            QMessageBox.warning(self.current_form, "Input Error",
                                "Please fill in all required fields")
            return

        try:
            # Call model to update
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
            # Get patient data for confirmation message
            patientData = self.patient_model.getPatientByID(patientID)

            if not patientData:
                QMessageBox.warning(self.view, "Error", "Patient data not found")
                return

            fullName = f"{patientData['PatientLname']}, {patientData['PatientFname']} {patientData['PatientMname'] or ''}".strip()

            # Confirm deletion
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
                # Delete the patient
                self.patient_model.deletePatient(patientID)

                QMessageBox.information(self.view, "Success",
                                        f"Patient {fullName} has been deleted successfully")

                self.loadPatientTable()

        except ValueError as ve:
            # Handle business rule violations (e.g., patient has transactions)
            QMessageBox.warning(self.view, "Cannot Delete", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Database Error",
                                 f"Error deleting patient: {e}")

    # Private helper methods
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

        # Check required fields (mname is optional)
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

        if not search_name:
            # If empty, load all patients
            QMessageBox.information(
                self.view,
                "Search Field Empty",
                "Please enter a name to search, or the table will show all patients."
            )
            self.loadPatientTable()
            return

        try:
            patients = self.patient_model.searchPatientByName(search_name)

            # Check if patients were found
            if not patients:
                QMessageBox.information(
                    self.view,
                    "No Patients Found",
                    f"No patients found matching: '{search_name}'"
                )
                # Clear the table
                self.view.patientTable.setRowCount(0)
                return

            # Patients found - show success message
            QMessageBox.information(
                self.view,
                "Patients Found",
                f"Found {len(patients)} patient(s) matching: '{search_name}'"
            )

            # Update table with search results
            table = self.view.patientTable
            header = table.horizontalHeader()

            # ✅ Set column resize modes for ALL 7 columns
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # PatientID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Patient FullName
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Sex
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Birthday
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # ContactNum
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Added At
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Updated At

            table.setRowCount(len(patients))

            # ✅ Populate table with search results INCLUDING timestamps
            for row, patient in enumerate(patients):
                fullName = f"{patient['PatientLname']}, {patient['PatientFname']} {patient['PatientMname'] or ''}".strip()
                birthday_str = patient['Birthday'].strftime('%Y-%m-%d') if patient['Birthday'] else ''

                table.setItem(row, 0, QTableWidgetItem(str(patient['PatientID'])))
                table.setItem(row, 1, QTableWidgetItem(fullName))
                table.setItem(row, 2, QTableWidgetItem(patient['Sex']))
                table.setItem(row, 3, QTableWidgetItem(birthday_str))
                table.setItem(row, 4, QTableWidgetItem(patient['ContactNumber']))

                # ✅ Add timestamp columns
                created_at_str = self._formatDateTime(patient.get('created_at'))
                updated_at_str = self._formatDateTime(patient.get('updated_at'))

                table.setItem(row, 5, QTableWidgetItem(created_at_str))
                table.setItem(row, 6, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to search patients: {e}")