

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
from PyQt6.QtWidgets import QApplication

# Import the Login view
from DentiCare.View.login_view import Login


def main():
    # Create the QApplication instance
    app = QApplication(sys.argv)

    # Create and show the login window
    login_window = Login()
    login_window.show()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()