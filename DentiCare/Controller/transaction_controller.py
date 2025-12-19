from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from decimal import Decimal
from DentiCare.Model.transaction_model import TransactionModel
from DentiCare.Model.patient_model import PatientModel
from DentiCare.Model.dashboard_model import DashboardModel
from DentiCare.Model.staff_model import StaffModel
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os




class TransactionController:
    #handles payment

    def __init__(self, view, current_staff_id):
        self.view = view  # Staff view
        self.transaction_model = TransactionModel()
        self.patient_model = PatientModel()
        self.dashboard_model = DashboardModel()
        self.current_staff_id = current_staff_id  # ID of logged-in staff
        self.selected_patient = None

        # Load initial data
        self.loadServices()
        self.loadDentists()

    def switchToTransactionsTab(self):
        """Switch to transaction tab with error handling"""
        try:
            print("DEBUG: Switching to transactions tab...")
            self.view.switchToTab(4)

            print("DEBUG: Loading total revenue...")
            try:
                self.loadTotalRevenueForTransactions()
            except Exception as e:
                print(f"WARNING: Failed to load revenue: {e}")
                # Continue even if revenue fails

            print("DEBUG: Loading records table...")
            self.loadRecordsTable()

            print("DEBUG: Tab loaded successfully!")

        except Exception as e:
            print(f"ERROR in switchToTransactionsTab: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.view,
                "Tab Load Error",
                f"Failed to load transactions tab:\n{str(e)}\n\nPlease check if database migration was run."
            )

    def loadServices(self):
        #load all service
        try:
            self.services = self.transaction_model.getAllServices()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load services: {e}")
            self.services = []

    def loadDentists(self):
        #load all dentist
        try:
            self.dentists = self.transaction_model.getAllDentists()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load dentists: {e}")
            self.dentists = []

    def searchPatientByID(self): #Search Patient For Payment Details Via ID
        #search patient via ID
        search_id = self.view.searchIDField.text().strip()

        if not search_id:
            QMessageBox.warning(self.view, "Input Error", "Please enter a Patient ID")
            return

        self._performPatientSearch(search_id) #call function to perform the search



    def _performPatientSearch(self, search_value):
        #perform patient search
        try:
            results = self.transaction_model.searchPatient(search_value)

            if not results:
                QMessageBox.information(self.view, "Not Found",
                                        "No patient found with the given information")
                self.clearPatientInfo()
                return

            # if len(results) > 1:
            #     # Multiple patients found - let user choose
            #     patient_names = [
            #         f"{p['PatientID']} - {p['PatientLname']}, {p['PatientFname']} {p['PatientMname'] or ''}"
            #         for p in results
            #     ]
            #     from PyQt6.QtWidgets import QInputDialog
            #     choice, ok = QInputDialog.getItem(
            #         self.view, "Multiple Patients Found",
            #         "Select a patient:", patient_names, 0, False
            #     )

                if ok and choice:
                    # Extract PatientID from choice
                    patient_id = choice.split(' - ')[0]
                    patient = next(p for p in results if p['PatientID'] == patient_id)
                    self._populatePatientInfo(patient)
                else:
                    return
            else:
                # Single patient found
                self._populatePatientInfo(results[0])

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Search failed: {e}")

    def _populatePatientInfo(self, patient):
       #populate the info fields
        self.selected_patient = patient

        self.view.fnameField.setText(patient['PatientFname'])
        self.view.mnameField.setText(patient['PatientMname'] or '')
        self.view.lnameField.setText(patient['PatientLname'])
        self.view.sexField.setText(patient['Sex'])
        self.view.contactField.setText(patient['ContactNumber'])

        # Set birthday
        birthday = patient['Birthday']
        if birthday:
            self.view.bdayField.setText(birthday.strftime('%Y-%m-%d'))
        else:
            self.view.bdayField.clear()

    def clearPatientInfo(self):
        #clear fields
        self.selected_patient = None
        self.view.fnameField.clear()
        self.view.mnameField.clear()
        self.view.lnameField.clear()
        self.view.sexField.clear()
        self.view.bdayField.clear()
        self.view.contactField.clear()

    def calculateTotal(self):
        #calculate total amount
        total = Decimal('0.00')

        for service_row in self.view.service_rows:
            try:
                # Get service price
                service_name = service_row.serviceField.currentText()
                if service_name == 'Services':  # Skip placeholder
                    continue

                # Find service price from loaded services
                service = next((s for s in self.services if s['ServiceName'] == service_name), None)#self.services from loadServices function
                if not service:
                    continue

                price = Decimal(str(service['Price']))
                quantity = service_row.quantityField.value()

                subtotal = price * quantity
                total += subtotal

            except Exception:
                continue

        # Update total field
        self.view.totalField.setText(f"{total:.2f}")
        return total

    def processPayment(self):
        """Process payment with notes and VAT"""
        # Validate patient selection
        if not self.selected_patient:
            QMessageBox.warning(self.view, "Validation Error",
                                "Please search and select a patient first")
            return

        # Validate service rows
        if not self.view.service_rows:
            QMessageBox.warning(self.view, "Validation Error",
                                "Please add at least one service")
            return

        # Get service details and validate
        service_details = []
        selected_dentist_id = None

        for service_row in self.view.service_rows:
            service_name = service_row.serviceField.currentText()
            dentist_name = service_row.dentistField.currentText()

            # Skip invalid rows
            if service_name == 'Services' or dentist_name == 'Dentists':
                QMessageBox.warning(self.view, "Validation Error",
                                    "Please complete all service fields (Service and Dentist)")
                return

            # Get service ID and full details
            service = next((s for s in self.services if s['ServiceName'] == service_name), None)
            if not service:
                QMessageBox.warning(self.view, "Error", f"Service '{service_name}' not found")
                return

            if not selected_dentist_id:
                dentist = next((d for d in self.dentists if dentist_name in d['DentistName']), None)
                if not dentist:
                    QMessageBox.warning(self.view, "Error", f"Dentist '{dentist_name}' not found")
                    return
                selected_dentist_id = dentist['StaffID']

            quantity = service_row.quantityField.value()

            # ✅ INCLUDE VAT DETAILS in service_details for receipt generation
            service_details.append({
                'service_id': service['ServiceID'],
                'service_name': service_name,
                'base_price': float(service.get('BasePrice', service['Price'])),  # ← Added
                'vat_amount': float(service.get('VATAmount', 0)),  # ← Added
                'price': float(service['Price']),
                'quantity': quantity
            })

            print("=== DEBUG: Service Details ===")
            for detail in service_details:
                print(f"Service: {detail.get('service_name')}")
                print(f"  Base Price: {detail.get('base_price')}")
                print(f"  VAT Amount: {detail.get('vat_amount')}")
                print(f"  Final Price: {detail.get('price')}")
                print(f"  Quantity: {detail.get('quantity')}")
            print("==============================")

        # Get transaction date
        transaction_date = self.view.dateField.date().toPyDate()

        # GET NOTES from the noteField (QTextEdit)
        notes = self.view.noteField.toPlainText().strip()
        if not notes:
            notes = None

        # Calculate total
        total_amount = self.calculateTotal()

        if total_amount <= 0:
            QMessageBox.warning(self.view, "Validation Error",
                                "Total amount must be greater than zero")
            return

        # Confirm transaction
        patient_name = f"{self.selected_patient['PatientLname']}, {self.selected_patient['PatientFname']}"

        # Include notes in confirmation if present
        confirm_msg = (f"Process payment for:\n\n"
                       f"Patient: {patient_name}\n"
                       f"Total Amount: ₱{total_amount:.2f}\n"
                       f"Date: {transaction_date}\n")

        if notes:
            confirm_msg += f"\nNotes: {notes[:100]}{'...' if len(notes) > 100 else ''}\n"

        confirm_msg += "\nContinue?"

        reply = QMessageBox.question(
            self.view,
            'Confirm Transaction',
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Process transaction
        try:
            # Prepare service details for database (only needs service_id and quantity)
            db_service_details = [
                {'service_id': s['service_id'], 'quantity': s['quantity']}
                for s in service_details
            ]

            # Create transaction in database
            transaction_id = self.transaction_model.createTransaction(
                dentist_id=selected_dentist_id,
                staff_id=self.current_staff_id,
                patient_id=self.selected_patient['PatientID'],
                total_amount=float(total_amount),
                transaction_date=transaction_date,
                service_details=db_service_details,
                notes=notes
            )

            # Generate receipt (service_details already includes VAT info)
            try:
                receipt_filename = self.generateReceipt(
                    transaction_id=transaction_id,
                    patient_name=patient_name,
                    total_amount=float(total_amount),
                    transaction_date=transaction_date,
                    service_details=service_details,  # ← Contains base_price, vat_amount, price
                    notes=notes
                )

                # Success message with receipt info
                from PyQt6.QtWidgets import QPushButton
                msg = QMessageBox(self.view)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(
                    f"Transaction completed successfully!\n\n"
                    f"Transaction ID: {transaction_id}\n"
                    f"Total Amount: ₱{total_amount:.2f}\n\n"
                    f"Receipt saved as:\n{receipt_filename}"
                )

                # Add Open Receipt button
                open_btn = msg.addButton("Open Receipt", QMessageBox.ButtonRole.ActionRole)
                ok_btn = msg.addButton(QMessageBox.StandardButton.Ok)

                msg.exec()

                # Open receipt if button was clicked
                if msg.clickedButton() == open_btn:
                    import subprocess
                    import platform

                    if platform.system() == 'Windows':
                        os.startfile(receipt_filename)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', receipt_filename])
                    else:  # Linux
                        subprocess.call(['xdg-open', receipt_filename])

            except Exception as e:
                QMessageBox.warning(
                    self.view,
                    "Receipt Generation Failed",
                    f"Transaction completed but receipt generation failed:\n{e}"
                )
                import traceback
                traceback.print_exc()

            # Clear form
            self.clearPaymentForm()

        except Exception as e:
            print("Transaction creation failed:", e)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.view, "Error", f"Failed to create transaction: {e}")
            return

    def clearPaymentForm(self):
        #clear fields
        self.clearPatientInfo()
        self.view.clear_all_services()
        self.view.totalField.clear()
        self.view.searchIDField.clear()
        # self.view.searchNameField.clear()
        self.view.dateField.setDate(QDate.currentDate())
        self.view.noteField.clear()

    def loadRecordsTable(self):
       #load records table (frontdesk)
        try:
            records = self.transaction_model.getAllTransactionRecords()

            table = self.view.recordsTable
            header = table.horizontalHeader()

            table.setColumnCount(10)  # Changed from 9 to 10

            # Resize behavior
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Transaction ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Processed By
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Patient ID
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Patient Name
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Dentist
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Service
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Price
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Total
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Date

            table.setRowCount(len(records))

            # Fill rows
            for row, rec in enumerate(records):
                date_str = rec['TransactionDate'].strftime('%Y-%m-%d')

                table.setItem(row, 0, QTableWidgetItem(str(rec['TransactionID'])))
                table.setItem(row, 1, QTableWidgetItem(rec['ProcessedBy']))
                table.setItem(row, 2, QTableWidgetItem(str(rec['PatientID'])))
                table.setItem(row, 3, QTableWidgetItem(rec['PatientName']))
                table.setItem(row, 4, QTableWidgetItem(rec['DentistName']))
                table.setItem(row, 5, QTableWidgetItem(rec['Service']))
                table.setItem(row, 6, QTableWidgetItem(f"₱{rec['PriceAtTransaction']:.2f}"))
                table.setItem(row, 7, QTableWidgetItem(str(rec['Quantity'])))
                table.setItem(row, 8, QTableWidgetItem(f"₱{rec['Total']:.2f}"))
                table.setItem(row, 9, QTableWidgetItem(date_str))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load records: {e}")

    # def viewTransactionDetails(self): # wa nay gamit
    #     """View details of selected transaction"""
    #     table = self.view.recordsTable
    #     row = table.currentRow()
    #
    #     if row < 0:
    #         QMessageBox.warning(self.view, "Selection Error",
    #                             "Please select a transaction from the table first.")
    #         return
    #
    #     transaction_id = table.item(row, 0).text()
    #
    #     try:
    #         transaction = self.transaction_model.getTransactionByID(transaction_id)
    #         details = self.transaction_model.getTransactionDetails(transaction_id)
    #
    #         if not transaction:
    #             QMessageBox.warning(self.view, "Error", "Transaction not found")
    #             return
    #
    #         # Build details message
    #         details_text = f"Transaction ID: {transaction['TransactionID']}\n"
    #         details_text += f"Date: {transaction['TransactionDate']}\n"
    #         details_text += f"Patient: {transaction['PatientName']}\n"
    #         details_text += f"Dentist: {transaction['DentistName']}\n\n"
    #         details_text += "Services:\n"
    #
    #         for detail in details:
    #             details_text += f"  - {detail['ServiceName']}: "
    #             details_text += f"₱{detail['PriceAtTransaction']:.2f} x {detail['Quantity']} = "
    #             details_text += f"₱{detail['Subtotal']:.2f}\n"
    #
    #         details_text += f"\nTotal Amount: ₱{transaction['TotalAmount']:.2f}"
    #
    #         QMessageBox.information(self.view, "Transaction Details", details_text)
    #
    #     except Exception as e:
    #         QMessageBox.critical(self.view, "Error", f"Failed to load transaction details: {e}")

    def searchRecordsByPatient(self):
        #search records by patient name
        search_id = self.view.searchField.text().strip()

        if not search_id:
            # If empty, load all records
            self.loadRecordsTable()
            return

        # Validate that input is numeric
        if not search_id.isdigit():
            QMessageBox.warning(
                self.view,
                "Invalid Input",
                "Please enter a valid Patient ID (numbers only)"
            )
            return

        try:
            records = self.transaction_model.searchTransactionRecordsByPatientID(int(search_id))

            # Check if records were found
            if not records:
                QMessageBox.information(
                    self.view,
                    "No Records Found",
                    f"No transaction records found for Patient ID: {search_id}"
                )
                # Clear the table
                self.view.recordsTable.setRowCount(0)
                return

            # Records found - show success message
            QMessageBox.information(
                self.view,
                "Records Found",
                f"Found {len(records)} transaction record(s) for Patient ID: {search_id}"
            )

            table = self.view.recordsTable
            header = table.horizontalHeader()

            table.setColumnCount(10)  # Increased to 10 columns to include Patient ID

            # Resize behavior
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Transaction ID
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Processed By
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Patient ID
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Patient Name
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Dentist
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Service
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Price
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Total
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Date

            table.setRowCount(len(records))

            for row, rec in enumerate(records):
                try:
                    # Handle date safely
                    date_obj = rec.get('TransactionDate')
                    if isinstance(date_obj, (str, bytes)):
                        date_str = str(date_obj)
                    elif date_obj:
                        date_str = date_obj.strftime('%Y-%m-%d')
                    else:
                        date_str = ''

                    # Convert numeric fields safely
                    price = float(rec.get('PriceAtTransaction') or 0)
                    total = float(rec.get('Total') or 0)

                    table.setItem(row, 0, QTableWidgetItem(str(rec.get('TransactionID', ''))))
                    table.setItem(row, 1, QTableWidgetItem(rec.get('ProcessedBy', '')))
                    table.setItem(row, 2, QTableWidgetItem(str(rec.get('PatientID', ''))))
                    table.setItem(row, 3, QTableWidgetItem(rec.get('PatientName', '')))
                    table.setItem(row, 4, QTableWidgetItem(rec.get('DentistName', '')))
                    table.setItem(row, 5, QTableWidgetItem(rec.get('Service', '')))
                    table.setItem(row, 6, QTableWidgetItem(f"₱{price:.2f}"))
                    table.setItem(row, 7, QTableWidgetItem(str(rec.get('Quantity', ''))))
                    table.setItem(row, 8, QTableWidgetItem(f"₱{total:.2f}"))
                    table.setItem(row, 9, QTableWidgetItem(date_str))
                except Exception as e:
                    print(f"Failed to populate row {row}: {e}")

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to search records: {e}")

    def generateReceipt(self, transaction_id, patient_name, total_amount,
                        transaction_date, service_details, notes=None):
        """Generate PDF receipt including VAT breakdown and notes"""
        try:


            staff_model = StaffModel()
            staff_info = staff_model.getStaffByID(self.current_staff_id)

            # Format staff name
            if staff_info:
                staff_name = f"{staff_info['StaffLname']}, {staff_info['StaffFname']}"
                if staff_info.get('StaffMname'):
                    staff_name += f" {staff_info['StaffMname']}"
            else:
                staff_name = "Unknown Staff"

            # Create receipts directory
            receipts_dir = os.path.join(os.getcwd(), 'receipts')
            if not os.path.exists(receipts_dir):
                os.makedirs(receipts_dir)

            # Generate filename
            filename = os.path.join(receipts_dir,
                                    f"Receipt_{transaction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1A1054'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1A1054'),
                spaceAfter=12
            )

            # Title
            title = Paragraph("<b>DENTICARE CLINIC</b>", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            # Receipt Header
            receipt_title = Paragraph("<b>PAYMENT RECEIPT</b>", heading_style)
            elements.append(receipt_title)
            elements.append(Spacer(1, 0.3 * inch))

            # Transaction Information
            info_data = [
                ['Transaction ID:', str(transaction_id)],
                ['Date:', transaction_date.strftime('%B %d, %Y')],
                ['Patient Name:', patient_name],
                ['Processed by:', staff_name],
            ]

            info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1A1054')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.4 * inch))

            # Services Header
            services_header = Paragraph("<b>SERVICES</b>", heading_style)
            elements.append(services_header)
            elements.append(Spacer(1, 0.1 * inch))

            # Services Table with VAT breakdown
            service_table_data = [['Service', 'Base Price', 'VAT', 'Price', 'Qty', 'Subtotal']]

            total_base = 0
            total_vat = 0
            total_amount_calc = 0

            for detail in service_details:
                service_name = detail['service_name']
                base_price = detail.get('base_price', 0)
                vat_amount = detail.get('vat_amount', 0)
                price = detail['price']
                quantity = detail['quantity']
                subtotal = price * quantity

                total_base += base_price * quantity
                total_vat += vat_amount * quantity
                total_amount_calc += subtotal

                # Show VAT breakdown only if VAT is applicable
                if vat_amount > 0:
                    vat_display = f"₱{vat_amount:.2f}"
                else:
                    vat_display = "N/A"

                service_table_data.append([
                    service_name,
                    f"₱{base_price:.2f}",
                    vat_display,
                    f"₱{price:.2f}",
                    str(quantity),
                    f"₱{subtotal:.2f}"
                ])

            # Add summary rows
            service_table_data.append(['', '', '', '', 'Subtotal:', f"₱{total_base:.2f}"])
            service_table_data.append(['', '', '', '', 'VAT (12%):', f"₱{total_vat:.2f}"])
            service_table_data.append(['', '', '', '', 'TOTAL:', f"₱{total_amount:.2f}"])

            service_table = Table(service_table_data,
                                  colWidths=[2.3 * inch, 0.9 * inch, 0.7 * inch, 0.9 * inch, 0.6 * inch, 1 * inch])
            service_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A1054')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Data rows
                ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -4), 9),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -4), 1, colors.grey),
                ('BOTTOMPADDING', (0, 1), (-1, -4), 6),
                ('TOPPADDING', (0, 1), (-1, -4), 6),

                # Summary rows (Subtotal, VAT, TOTAL)
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -3), (-1, -2), 10),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.grey),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1A1054')),
                ('BOTTOMPADDING', (0, -3), (-1, -1), 6),
                ('TOPPADDING', (0, -3), (-1, -1), 6),
            ]))
            elements.append(service_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Notes section
            if notes:
                notes_header = Paragraph("<b>NOTES</b>", heading_style)
                elements.append(notes_header)
                elements.append(Spacer(1, 0.1 * inch))

                notes_style = ParagraphStyle(
                    'NotesStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    leftIndent=20,
                    rightIndent=20,
                    spaceAfter=10
                )

                notes_paragraph = Paragraph(notes.replace('\n', '<br/>'), notes_style)
                elements.append(notes_paragraph)
                elements.append(Spacer(1, 0.3 * inch))

            # VAT Information Footer
            vat_info_style = ParagraphStyle(
                'VATInfo',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=10
            )

            vat_info = Paragraph(
                "<b>VAT-Registered Business</b><br/>"
                "TIN: [Your TIN Here]<br/>"
                "VAT rate of 12% is already included in the final price",
                vat_info_style
            )
            elements.append(vat_info)

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            footer = Paragraph("Thank you for choosing DentiCare Clinic!<br/>For concerns, please contact us.",
                               footer_style)
            elements.append(footer)

            # Build PDF
            doc.build(elements)

            return filename

        except Exception as e:
            print(f"DEBUG: Exception in generateReceipt: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate receipt: {e}")

    def loadTotalRevenueForTransactions(self):
        """Load total revenue and display in transaction tab"""
        try:
            total_revenue = self.dashboard_model.getTotalRevenue()

            # Format the revenue with peso sign and 2 decimal places
            formatted_revenue = f"₱{total_revenue:,.2f}"

            # Update the line edit field in your transaction tab
            # Adjust the field name based on your UI file
            if hasattr(self.view, 'totalRevenueField'):
                self.view.totalRevenueField.setText(formatted_revenue)
            elif hasattr(self.view, 'revenueField'):
                self.view.revenueField.setText(formatted_revenue)
            else:
                print("WARNING: Revenue display field not found in view")

            print(f"DEBUG: Total revenue loaded: {formatted_revenue}")

        except Exception as e:
            print(f"ERROR loading revenue: {e}")
            import traceback
            traceback.print_exc()
            # Don't show error to user, just log it
            # Set field to 0 if it exists
            if hasattr(self.view, 'totalRevenueField'):
                self.view.totalRevenueField.setText("₱0.00")
            elif hasattr(self.view, 'revenueField'):
                self.view.revenueField.setText("₱0.00")