import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap
from DentiCare.View.admin_pov import Admin
from DentiCare.View.staff_pov import Staff
from DentiCare.Controller.authentication_controller import AuthenticationController


def get_resource_path(filename):
    # Get the directory where THIS file (login_view.py) is located
    current_file = Path(__file__).resolve()
    # Go up to project root: View -> DentiCare -> DentalClinic
    project_root = current_file.parent.parent.parent
    return str(project_root / filename)


class Login(QDialog):
    def __init__(self):
        super().__init__()
        # Use absolute path for UI file
        loadUi(get_resource_path("DentiCare/ui/login.ui"), self)

        self.auth_controller = AuthenticationController()
        self._setup_logo()
        self.loginBtn.clicked.connect(self.handle_login)

    def _setup_logo(self):
        """Setup logo display"""
        # Use absolute path for image
        logo_path = get_resource_path("DentiCare/assets/Logo.png")
        
        # Debug: Print to verify path
        print(f"Loading logo from: {logo_path}")
        print(f"File exists: {Path(logo_path).exists()}")
        
        pixmap = QPixmap(logo_path)
        
        if pixmap.isNull():
            print("❌ ERROR: Failed to load logo image!")
            print(f"Make sure Logo.png exists in: {Path(logo_path).parent}")
            return
        else:
            print("✅ Logo loaded successfully")
        
        scaled = pixmap.scaled(
            self.logo_holder.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.logo_holder.setPixmap(scaled)
        self.logo_holder.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def handle_login(self):
        """Handles login when loginBtn is clicked"""
        username = self.usernameField.text().strip()
        password = self.PasswordField.text().strip()

        if not username or not password:
            self.show_error("Input Error", "Please enter both username and password")
            return

        result = self.auth_controller.login(username, password)

        if result['success']:
            self.open_main_window(result['staff_id'], result['role'])
        else:
            self.show_error("Login Failed", result['message'])

    def open_main_window(self, staff_id, role):
        """Open window based on the role"""
        if role == 'admin':
            self.admin_window = Admin(staff_id)
            self.admin_window.show()
        elif role == 'frontdesk':
            self.staff_window = Staff(staff_id)
            self.staff_window.show()
        else:
            self.show_error("Unknown Role", f"Role '{role}' is not recognized")
            return

        self.close()

    def show_error(self, title, message):
        """Display messages"""
        QMessageBox.warning(self, title, message)