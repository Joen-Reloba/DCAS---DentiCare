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

    def connect_add_button(self, serviceFormAddBtn):
        serviceFormAddBtn.clicked.connect(self.addService)

    def switchToServiceTab(self):
        """Switch to service tab"""
        self.view.switchToTab(3)
        self.loadServiceTable()

    def showServiceAddForm(self):
        """Show form to add new service"""
        self.addForm = QDialog(self.view)
        loadUi("DentiCare/ui/serviceAddForm.ui", self.addForm)

        # Set default VAT rate to 12%
        if hasattr(self.addForm, 'vatRateField'):
            self.addForm.vatRateField.setValue(12.00)

        # Set VAT checkbox as checked by default
        if hasattr(self.addForm, 'vatCheckBox'):
            self.addForm.vatCheckBox.setChecked(True)

        # ✅ Initialize finalPriceDisplay_2
        if hasattr(self.addForm, 'finalPriceDisplay_2'):
            self.addForm.finalPriceDisplay_2.setText("₱0.00")

        # Connect VAT calculation signals
        self._connectVATCalculationAdd()

        self.addForm.serviceFormAddBtn.clicked.connect(self.addService)
        self.addForm.exec()

    def _connectVATCalculationAdd(self):
        """Connect signals for automatic VAT calculation in ADD form"""
        # ✅ Check for correct field name: finalPriceDisplay_2
        if not all([
            hasattr(self.addForm, 'basePriceField'),
            hasattr(self.addForm, 'vatCheckBox'),
            hasattr(self.addForm, 'vatRateField'),
            hasattr(self.addForm, 'finalPriceDisplay_2')
        ]):
            print("Warning: Not all VAT fields found in Add form")
            return

        # Connect signals
        self.addForm.basePriceField.textChanged.connect(self._updateFinalPriceAdd)
        self.addForm.vatCheckBox.stateChanged.connect(self._updateVATFieldsAdd)
        self.addForm.vatRateField.valueChanged.connect(self._updateFinalPriceAdd)

        # Initial state
        self._updateVATFieldsAdd()
        self._updateFinalPriceAdd()

    def _updateVATFieldsAdd(self):
        """Enable/disable VAT rate field based on checkbox in ADD form"""
        is_vat_checked = self.addForm.vatCheckBox.isChecked()
        self.addForm.vatRateField.setEnabled(is_vat_checked)
        self._updateFinalPriceAdd()

    def _updateFinalPriceAdd(self):
        """Calculate and display final price with VAT in ADD form"""
        # ✅ USE CORRECT FIELD NAME: finalPriceDisplay_2
        if not hasattr(self.addForm, 'finalPriceDisplay_2'):
            return

        try:
            base_price_text = self.addForm.basePriceField.text().strip()
            base_price = float(base_price_text) if base_price_text else 0
            is_vat = self.addForm.vatCheckBox.isChecked()
            vat_rate = self.addForm.vatRateField.value()

            if is_vat:
                vat_amount = base_price * (vat_rate / 100)
                final_price = base_price + vat_amount
                display_text = f"₱{final_price:.2f}"
                tooltip = f"Base: ₱{base_price:.2f}\nVAT ({vat_rate:.0f}%): ₱{vat_amount:.2f}\nFinal: ₱{final_price:.2f}"
                self.addForm.finalPriceDisplay_2.setText(display_text)
                self.addForm.finalPriceDisplay_2.setToolTip(tooltip)
            else:
                display_text = f"₱{base_price:.2f}"
                tooltip = "No VAT applied"
                self.addForm.finalPriceDisplay_2.setText(display_text)
                self.addForm.finalPriceDisplay_2.setToolTip(tooltip)
        except ValueError:
            self.addForm.finalPriceDisplay_2.setText("₱0.00")
            self.addForm.finalPriceDisplay_2.setToolTip("")

    def getServiceInfo(self):
        """Get service information from form"""
        serviceName = self.addForm.serviceNameField.text()
        basePrice = self.addForm.basePriceField.text()

        # Get VAT information
        isVATApplicable = True
        vatRate = 12.00

        if hasattr(self.addForm, 'vatCheckBox'):
            isVATApplicable = self.addForm.vatCheckBox.isChecked()

        if hasattr(self.addForm, 'vatRateField'):
            vatRate = self.addForm.vatRateField.value()

        return (serviceName, basePrice, isVATApplicable, vatRate)

    def addService(self):
        """Add new service"""
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
        """Load services table with VAT information"""
        try:
            serviceList = self.service_model.getAllService()
            table = self.view.servicesTable
            header = table.horizontalHeader()

            # Set columns: ID, Name, Base Price, VAT, Final Price, Added At, Updated At
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                'ID', 'Service Name', 'Base Price', 'VAT', 'Final Price', 'Added At', 'Updated At'
            ])

            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Base Price
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # VAT
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Final Price
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Added At
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Updated At

            table.setRowCount(len(serviceList))

            for row, svc in enumerate(serviceList):
                table.setItem(row, 0, QTableWidgetItem(str(svc["ServiceID"])))
                table.setItem(row, 1, QTableWidgetItem(svc["ServiceName"]))
                table.setItem(row, 2, QTableWidgetItem(f"₱{float(svc['BasePrice']):.2f}"))

                # VAT column
                if svc['IsVATApplicable']:
                    vat_text = f"₱{float(svc['VATAmount']):.2f} ({float(svc['VATRate']):.0f}%)"
                else:
                    vat_text = "N/A"
                table.setItem(row, 3, QTableWidgetItem(vat_text))

                table.setItem(row, 4, QTableWidgetItem(f"₱{float(svc['FinalPrice']):.2f}"))

                created_at_str = self._formatDateTime(svc.get('created_at'))
                updated_at_str = self._formatDateTime(svc.get('updated_at'))

                table.setItem(row, 5, QTableWidgetItem(created_at_str))
                table.setItem(row, 6, QTableWidgetItem(updated_at_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load services: {e}")

    def getSelectedService(self):
        """Get selected service ID"""
        row = self.view.servicesTable.currentRow()
        if row < 0:
            QMessageBox.warning(self.view, "Selection Error", "Please select a service first.")
            return None
        return self.view.servicesTable.item(row, 0).text()

    def showServiceUpdateForm(self):
        """Show form to update service"""
        serviceID = self.getSelectedService()
        if not serviceID:
            return

        try:
            data = self.service_model.getServiceByID(serviceID)
            if not data:
                QMessageBox.warning(self.view, "Error", "Service not found.")
                return

            self.updateForm = QDialog(self.view)
            loadUi("DentiCare/ui/serviceUpdateForm.ui", self.updateForm)

            # Set basic fields
            self.updateForm.serviceIDField.setText(serviceID)
            self.updateForm.serviceNameField.setText(data["ServiceName"])

            # ✅ USE CORRECT FIELD NAME: basePriceField_2 for base price in UPDATE form
            if hasattr(self.updateForm, 'basePriceField_2'):
                self.updateForm.basePriceField_2.setText(str(data["BasePrice"]))
            else:
                # Fallback to basePriceField if _2 doesn't exist
                self.updateForm.basePriceField.setText(str(data["BasePrice"]))

            # Set VAT information
            if hasattr(self.updateForm, 'vatCheckBox'):
                self.updateForm.vatCheckBox.setChecked(data["IsVATApplicable"])

            if hasattr(self.updateForm, 'vatRateField'):
                self.updateForm.vatRateField.setValue(float(data["VATRate"]))

            # Connect VAT calculation signals for UPDATE form
            self._connectVATCalculationUpdate()

            self.updateForm.serviceFormUpdateBtn.clicked.connect(
                lambda: self.updateService(serviceID)
            )

            self.updateForm.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error opening update form: {e}")
            import traceback
            traceback.print_exc()

    def _connectVATCalculationUpdate(self):
        """Connect signals for automatic VAT calculation in UPDATE form"""
        # ✅ Check for correct field names: basePriceField_2 and finalPriceDisplay
        # Try basePriceField_2 first, fallback to basePriceField
        base_price_field = None
        if hasattr(self.updateForm, 'basePriceField_2'):
            base_price_field = self.updateForm.basePriceField_2
        elif hasattr(self.updateForm, 'basePriceField'):
            base_price_field = self.updateForm.basePriceField

        if not all([
            base_price_field is not None,
            hasattr(self.updateForm, 'vatCheckBox'),
            hasattr(self.updateForm, 'vatRateField'),
            hasattr(self.updateForm, 'finalPriceDisplay')
        ]):
            print("Warning: Not all VAT fields found in Update form")
            return

        # Connect signals
        base_price_field.textChanged.connect(self._updateFinalPriceUpdate)
        self.updateForm.vatCheckBox.stateChanged.connect(self._updateVATFieldsUpdate)
        self.updateForm.vatRateField.valueChanged.connect(self._updateFinalPriceUpdate)

        # Initial state
        self._updateVATFieldsUpdate()
        self._updateFinalPriceUpdate()

    def _updateVATFieldsUpdate(self):
        """Enable/disable VAT rate field based on checkbox in UPDATE form"""
        is_vat_checked = self.updateForm.vatCheckBox.isChecked()
        self.updateForm.vatRateField.setEnabled(is_vat_checked)
        self._updateFinalPriceUpdate()

    def _updateFinalPriceUpdate(self):
        """Calculate and display final price with VAT in UPDATE form"""
        if not hasattr(self.updateForm, 'finalPriceDisplay'):
            return

        try:
            # ✅ Get base price from correct field: basePriceField_2 or basePriceField
            base_price_text = ""
            if hasattr(self.updateForm, 'basePriceField_2'):
                base_price_text = self.updateForm.basePriceField_2.text().strip()
            elif hasattr(self.updateForm, 'basePriceField'):
                base_price_text = self.updateForm.basePriceField.text().strip()

            base_price = float(base_price_text) if base_price_text else 0
            is_vat = self.updateForm.vatCheckBox.isChecked()
            vat_rate = self.updateForm.vatRateField.value()

            if is_vat:
                vat_amount = base_price * (vat_rate / 100)
                final_price = base_price + vat_amount
                display_text = f"₱{final_price:.2f}"
                tooltip = f"Base: ₱{base_price:.2f}\nVAT ({vat_rate:.0f}%): ₱{vat_amount:.2f}\nFinal: ₱{final_price:.2f}"
                self.updateForm.finalPriceDisplay.setText(display_text)
                self.updateForm.finalPriceDisplay.setToolTip(tooltip)
            else:
                display_text = f"₱{base_price:.2f}"
                tooltip = "No VAT applied"
                self.updateForm.finalPriceDisplay.setText(display_text)
                self.updateForm.finalPriceDisplay.setToolTip(tooltip)
        except ValueError:
            self.updateForm.finalPriceDisplay.setText("₱0.00")
            self.updateForm.finalPriceDisplay.setToolTip("")

    def updateService(self, serviceID):
        """Update service information"""
        name = self.updateForm.serviceNameField.text().strip()

        # ✅ Get base price from correct field: basePriceField_2 or basePriceField
        basePrice = ""
        if hasattr(self.updateForm, 'basePriceField_2'):
            basePrice = self.updateForm.basePriceField_2.text().strip()
        elif hasattr(self.updateForm, 'basePriceField'):
            basePrice = self.updateForm.basePriceField.text().strip()

        if name == "" or basePrice == "":
            QMessageBox.warning(self.updateForm, "Input Error", "Please fill in all required fields")
            return

        # Get VAT information
        isVATApplicable = True
        vatRate = 12.00

        if hasattr(self.updateForm, 'vatCheckBox'):
            isVATApplicable = self.updateForm.vatCheckBox.isChecked()

        if hasattr(self.updateForm, 'vatRateField'):
            vatRate = self.updateForm.vatRateField.value()

        try:
            self.service_model.updateService(serviceID, name, basePrice, isVATApplicable, vatRate)
            QMessageBox.information(self.view, "Success", "Service updated successfully")
            self.updateForm.close()
            self.loadServiceTable()

        except Exception as e:
            QMessageBox.critical(self.updateForm, "Database Error", f"Error updating service: {e}")

    def deleteService(self):
        """Delete selected service"""
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
                # QMessageBox.critical(self.view, "Database Error", f"Error deleting service: {e}")
                QMessageBox.critical(self.view, "Delete Not Allowed",
    "This service cannot be deleted because it is already used in one or more transactions.\n\n"
    "To maintain record integrity, services linked to transactions cannot be removed.")