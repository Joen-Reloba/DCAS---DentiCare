import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap
from DentiCare.Controller.staff_controller import StaffTabController
from DentiCare.Controller.account_controller import AccountTabController
from DentiCare.Controller.service_controller import ServiceTabController
from DentiCare.Controller.dashboard_controller import DashboardTabController
from DentiCare.Controller.transaction_controller import TransactionController
from DentiCare.Controller.report_controller import ReportController
from pathlib import Path

# def get_resource_path(filename):
#     """Get absolute path to resource file in project root"""
#     current_file = Path(__file__).resolve()
#     project_root = current_file.parent.parent.parent  # View -> DentiCare -> DentalClinic
#     return str(project_root / filename)


def get_resource_path(filename):
    """Get absolute path to resource file in project root"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return str(project_root / filename)


class Admin(QMainWindow):
    def __init__(self, staff_id):
        super().__init__()

        loadUi(get_resource_path("DentiCare/ui/adminui.ui"), self)
        self.setFixedSize(1089, 596)

        self.current_staff_id = staff_id
        print(self.current_staff_id)

        self._setupLogo()
        self.stackedWidget.setCurrentIndex(0)
        self.dashboardBtn.setChecked(True)

        # Instantiate Controllers
        self.dashboard_controller = DashboardTabController(self)
        self.staff_controller = StaffTabController(self)
        self.account_controller = AccountTabController(self)
        self.service_controller = ServiceTabController(self)
        self.transaction_controller = TransactionController(self, self.current_staff_id)
        self.report_controller = ReportController(self)

        # Connect UI events
        self._connectNavigationButtons()
        self._connectStaffButtons()
        self._connectAccountButtons()
        self._connectServiceButtons()
        self._connectTransactionButtons()

        self.dashboard_controller.loadDashboardData()

    def _setupLogo(self):
        """Setup logo for window"""
        pixmap = QPixmap(get_resource_path("DentiCare/assets/icon_logo.png"))
        self.admin_logo_holder.setPixmap(
            pixmap.scaled(
                self.admin_logo_holder.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.admin_logo_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _connectNavigationButtons(self):
        """Connect navigation buttons to controllers"""
        self.dashboardBtn.clicked.connect(
            lambda: self.dashboard_controller.switchToDashboard()
        )
        self.staffBtn.clicked.connect(
            lambda: self.staff_controller.switchToStaffTab()
        )
        self.accountBtn.clicked.connect(
            lambda: self.account_controller.switchToAccountTab()
        )
        self.serviceBtn.clicked.connect(
            lambda: self.service_controller.switchToServiceTab()
        )
        self.transactionBtn.clicked.connect(
            lambda: self.transaction_controller.switchToTransactionsTab()
        )
        self.logoutBtn.clicked.connect(self.logout)

    def _connectStaffButtons(self):
        self.staffAddBtn.clicked.connect(self.staff_controller.showAddForm)
        self.staffUpdateBtn.clicked.connect(self.staff_controller.showUpdateForm)
        self.staffDelBtn.clicked.connect(self.staff_controller.deleteStaff)

    def _connectAccountButtons(self):
        self.accountAddBtn.clicked.connect(self.account_controller.showAddForm)
        self.accountUpdateBtn.clicked.connect(self.account_controller.showUpdateForm)
        self.accountDelBtn.clicked.connect(self.account_controller.deleteAccount)

    def _connectServiceButtons(self):
        self.serviceAddBtn.clicked.connect(self.service_controller.showServiceAddForm)
        self.serviceUpdateBtn.clicked.connect(self.service_controller.showServiceUpdateForm)
        self.serviceDelBtn.clicked.connect(self.service_controller.deleteService)

    def _connectTransactionButtons(self):
        self.generateReportBtn.clicked.connect(self.report_controller.showGenerateReportForm)

    def switchToTab(self, index):
        """Switch to a specific tab"""
        self.stackedWidget.setCurrentIndex(index)

    def getStaffTable(self):
        return self.staffTable

    def getAccountTable(self):
        return self.accountTable

    def getServiceTable(self):
        return self.servicesTable

    def createDialog(self, ui_file, parent=None):
        """Create dialog when controller calls"""
        dialog = QDialog(parent or self)
        # ✅ Use absolute path
        loadUi(get_resource_path(ui_file), dialog)
        return dialog

    def logout(self):
        """Handle logout"""
        from DentiCare.View.login_view import Login
        self.login_window = Login()
        self.login_window.show()
        self.close()