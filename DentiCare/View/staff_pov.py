import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget,
                             QVBoxLayout, QComboBox, QLineEdit, QSpinBox,
                             QPushButton, QHBoxLayout)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap
from DentiCare.Controller.patient_controller import PatientTabController
from DentiCare.Controller.transaction_controller import TransactionController
from DentiCare.Controller.report_controller import ReportController


def get_resource_path(filename):
    """Get absolute path to resource file in project root"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent  # View -> DentiCare -> DentalClinic
    return str(project_root / filename)


class ServiceRowWidget(QWidget):
    """A single service row for the dental clinic form."""

    remove_requested = pyqtSignal(QWidget)

    def __init__(self, services_list, dentists_list, parent=None):
        super().__init__(parent)

        # --- Service ComboBox ---
        self.serviceField = QComboBox()
        self.serviceField.addItem('Services')  # placeholder

        # Add services from database
        for service in services_list:
            self.serviceField.addItem(service['ServiceName'])

        self.serviceField.setCurrentIndex(0)
        self.serviceField.model().item(0).setEnabled(False)

        # --- Dentist ComboBox ---
        self.dentistField = QComboBox()
        self.dentistField.addItem('Dentists')  # placeholder

        # Add dentists from database
        for dentist in dentists_list:
            self.dentistField.addItem(dentist['DentistName'])

        self.dentistField.setCurrentIndex(0)
        self.dentistField.model().item(0).setEnabled(False)

        combo_style = """
        QComboBox {
            border: 2px solid #1A1054;
            border-radius: 5px;
            padding: 3px;
            background-color: rgb(255, 255, 255);
            color: rgb(26, 16, 84);
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #1A1054;
            selection-background-color: #1A1054;
            color: black;
        }
        """
        self.serviceField.setStyleSheet(combo_style)
        self.dentistField.setStyleSheet(combo_style)

        # --- Price Display (Read-only) ---
        self.priceField = QLineEdit()
        self.priceField.setPlaceholderText("Price")
        self.priceField.setFixedWidth(80)
        self.priceField.setReadOnly(True)
        lineedit_style = """
        QLineEdit {
            border: 2px solid #1A1054;
            border-radius: 5px;
            padding: 3px;
            background-color: rgb(240, 240, 240);
            color: rgb(26, 16, 84);
        }
        """
        self.priceField.setStyleSheet(lineedit_style)

        # --- Quantity SpinBox ---
        self.quantityField = QSpinBox()
        self.quantityField.setMinimum(1)
        self.quantityField.setMaximum(99)
        self.quantityField.setValue(1)
        self.quantityField.setFixedWidth(70)
        self.quantityField.setFixedHeight(28)

        spinbox_style = """
        QSpinBox {
            border: 2px solid #1A1054;
            border-radius: 5px;
            padding: 2px 4px;
            background-color: rgb(255, 255, 255);
        }
        QSpinBox::up-button, QSpinBox::down-button {
            width: 20px;
            height: 14px;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 8px;
            height: 8px;
        }
        """
        self.quantityField.setStyleSheet(spinbox_style)

        # --- Remove Button ---
        self.removeBtn = QPushButton("X")
        self.removeBtn.setFixedWidth(30)
        self.removeBtn.setStyleSheet(
            "QPushButton { background-color: red; color: white; border-radius: 5px; }"
        )
        self.removeBtn.clicked.connect(self._request_remove)

        # --- Layout ---
        layout = QHBoxLayout()
        layout.addWidget(self.serviceField)
        layout.addWidget(self.dentistField)
        layout.addWidget(self.priceField)
        layout.addWidget(self.quantityField)
        layout.addWidget(self.removeBtn)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        self.setFixedWidth(450)

        self.setLayout(layout)

        # Store services list for price lookup
        self.services_list = services_list

        # Connect service change to update price
        self.serviceField.currentTextChanged.connect(self._update_price)
        self.quantityField.valueChanged.connect(self._update_price)

    def _update_price(self):
        """Update price field with VAT breakdown (includes tooltip)"""
        service_name = self.serviceField.currentText()
        if service_name == 'Services':
            self.priceField.clear()
            self.priceField.setToolTip("")
            return

        # Find service in services list
        service = next((s for s in self.services_list if s['ServiceName'] == service_name), None)
        if service:
            # Get price components
            final_price = service['Price']  # This is the final price with VAT
            base_price = service.get('BasePrice', final_price)
            vat_amount = service.get('VATAmount', 0)
            quantity = self.quantityField.value()

            # Calculate subtotal
            subtotal = final_price * quantity
            self.priceField.setText(f"₱{subtotal:.2f}")

            # Set tooltip with VAT breakdown
            if vat_amount > 0:
                tooltip = (f"Per Unit:\n"
                           f"Base: ₱{base_price:.2f}\n"
                           f"VAT (12%): ₱{vat_amount:.2f}\n"
                           f"Price: ₱{final_price:.2f}\n"
                           f"\n"
                           f"Quantity: {quantity}\n"
                           f"Total: ₱{subtotal:.2f}")
                self.priceField.setToolTip(tooltip)
            else:
                tooltip = (f"Per Unit: ₱{final_price:.2f}\n"
                           f"Quantity: {quantity}\n"
                           f"Total: ₱{subtotal:.2f}\n"
                           f"(No VAT)")
                self.priceField.setToolTip(tooltip)

    def _request_remove(self):
        self.remove_requested.emit(self)


class Staff(QMainWindow):
    """VIEW - Only handles UI display and user interactions"""

    def __init__(self, staff_id):  # Pass logged-in staff ID
        super().__init__()
        try:
            loadUi(get_resource_path("DentiCare/ui/staffui.ui"), self)
            self.setFixedSize(1121, 601)

            self.current_staff_id = staff_id

            print(self.current_staff_id)

            # Setup UI
            self._setup_ui()

            self.patientsBtn.setChecked(True)

            # Initialize controllers
            self.patient_controller = PatientTabController(self)
            self.transaction_controller = TransactionController(self, self.current_staff_id)
            self.report_controller = ReportController(self)

            # Connect signals
            self._connect_signals()

            # Load initial data
            self.patient_controller.loadPatientTable()

            # Set current date in date field
            self.dateField.setDate(QDate.currentDate())
        except Exception as e:
            print(f"ERROR in Staff.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _setup_ui(self):
        """Setup UI elements"""
        pixmap = QPixmap(get_resource_path("DentiCare/assets/icon_logo.png"))
        self.staff_logo_holder.setPixmap(
            pixmap.scaled(
                self.staff_logo_holder.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.staff_logo_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.setCurrentIndex(0)

        self.servicescrollArea.setWidgetResizable(True)

        # --- SCROLL AREA SETUP ---
        self.scrollContent = QWidget()
        self.servicesLayout = QVBoxLayout(self.scrollContent)
        self.servicesLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.servicescrollArea.setWidget(self.scrollContent)

        # List to hold rows
        self.service_rows = []

    def _connect_signals(self):
        """Connect all UI signals to controller methods"""
        # Tab switching
        self.patientsBtn.clicked.connect(self.switchToPatientTab)
        self.recordsBtn.clicked.connect(self.switchToRecordsTab)
        self.paymentBtn.clicked.connect(self.switchToPaymentTab)

        # Patient operations
        self.patientAddBtn.clicked.connect(self.patient_controller.showPatientAddForm)
        self.patientUpdateBtn.clicked.connect(self.patient_controller.showPatientUpdateForm)
        self.patientDelBtn.clicked.connect(self.patient_controller.deletePatient)
        self.patientnameSearchBtn.clicked.connect(self.patient_controller.searchPatientByName)

        # Payment Tab operations
        self.addServiceBtn.clicked.connect(self.add_service_row)
        self.IDSearchBtn.clicked.connect(self.transaction_controller.searchPatientByID)
        self.totalField.returnPressed.connect(self.transaction_controller.processPayment)
        self.processBtn.clicked.connect(self.transaction_controller.processPayment)

        # Records Tab Operations , Connect Search Patient Record Button
        self.patientrecordSearchBtn.clicked.connect(self.transaction_controller.searchRecordsByPatient)
        self.exportRecordBtn.clicked.connect(self.report_controller.exportRecordsTableToPDF)

        # Logout
        self.logoutBtn.clicked.connect(self.logout)

    # Service row management (UI-only logic)
    def add_service_row(self):
        """Add a new service row to the scroll area"""
        service_row = ServiceRowWidget(
            self.transaction_controller.services,
            self.transaction_controller.dentists,
            self
        )
        service_row.removeBtn.clicked.connect(lambda: self.remove_service_row(service_row))

        # Connect quantity and service changes to recalculate total
        service_row.quantityField.valueChanged.connect(self.transaction_controller.calculateTotal)
        service_row.serviceField.currentTextChanged.connect(self.transaction_controller.calculateTotal)

        self.servicesLayout.addWidget(service_row)
        self.service_rows.append(service_row)

    def remove_service_row(self, service_row):
        """Remove a service row from the scroll area layout"""
        self.servicesLayout.removeWidget(service_row)
        if service_row in self.service_rows:
            self.service_rows.remove(service_row)
        service_row.deleteLater()

        # Recalculate total after removing
        self.transaction_controller.calculateTotal()

    def clear_all_services(self):
        # Make a copy of the list to safely iterate
        for row in self.service_rows[:]:
            # Remove the widget safely from the layout
            row.setParent(None)
        # finally clear the list
        self.service_rows.clear()

    # Navigation methods
    def switchToPatientTab(self):
        """Switch to patient tab and refresh data"""
        self.stackedWidget.setCurrentIndex(0)
        self.patient_controller.loadPatientTable()

    def switchToRecordsTab(self):
        """Switch to records tab and refresh data"""
        self.stackedWidget.setCurrentIndex(1)
        self.transaction_controller.loadRecordsTable()

    def switchToPaymentTab(self):
        """Switch to payment tab"""
        self.stackedWidget.setCurrentIndex(2)
        # Clear form when switching to payment tab
        self.transaction_controller.clearPaymentForm()

    def logout(self):
        """Logout and return to login screen"""
        from DentiCare.View.login_view import Login
        self.login_window = Login()
        self.login_window.show()
        self.close()