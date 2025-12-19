from PyQt6.QtWidgets import QMessageBox, QDialog
from PyQt6.uic import loadUi
from DentiCare.Model.report_model import ReportModel
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from collections import defaultdict
import os



from DentiCare.Model.transaction_model import TransactionModel


class ReportController:
    #handles report generation

    def __init__(self, view):
        self.view = view  # Admin view
        self.report_model = ReportModel()
        self.transaction_model=TransactionModel()

    def showGenerateReportForm(self):
        #pop up report form
        self.reportForm = QDialog(self.view)
        loadUi("DentiCare/ui/reportForm.ui", self.reportForm)

        # Set current year as default
        self.reportForm.yearField.setValue(datetime.now().year)

        # Connect generate button
        self.reportForm.reportFormGenerateBtn.clicked.connect(self.generateMonthlyReport)

        self.reportForm.exec()

    def generateMonthlyReport(self):
        #generate monthy report
        try:
            # Get selected month and year
            month_name = self.reportForm.monthField.currentText()
            year = self.reportForm.yearField.value()

            # Convert month name to number
            months = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month = months[month_name]

            # Get data from database
            transactions = self.report_model.getTransactionsByMonthYear(month, year)
            service_revenue = self.report_model.getRevenueByServiceForMonth(month, year)
            total_data = self.report_model.getTotalRevenueForMonth(month, year)

            if not transactions:
                QMessageBox.information(
                    self.reportForm,
                    "No Data",
                    f"No transactions found for {month_name} {year}"
                )
                return

            # Generate PDF
            filename = self._createMonthlyReportPDF(
                month_name, year, transactions, service_revenue, total_data
            )

            # Success message with option to open
            msg = QMessageBox(self.reportForm)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Report Generated")
            msg.setText(
                f"Monthly report for {month_name} {year} has been generated!\n\n"
                f"Total Revenue: ₱{total_data['TotalRevenue']:,.2f}\n"
                f"Total Transactions: {total_data['TransactionCount']}\n\n"
                f"Report saved as:\n{filename}"
            )

            open_btn = msg.addButton("Open Report", QMessageBox.ButtonRole.ActionRole)
            ok_btn = msg.addButton(QMessageBox.StandardButton.Ok)

            msg.exec()

            # Open report if button clicked
            if msg.clickedButton() == open_btn:
                import subprocess
                import platform

                if platform.system() == 'Windows':
                    os.startfile(filename)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', filename])
                else:  # Linux
                    subprocess.call(['xdg-open', filename])

            # Close the form
            self.reportForm.accept()

        except Exception as e:
            QMessageBox.critical(
                self.reportForm,
                "Error",
                f"Failed to generate report: {e}"
            )
            print(f"Report generation error: {e}")
            import traceback
            traceback.print_exc()

    def _createMonthlyReportPDF(self, month_name, year, transactions, service_revenue, total_data):
       #create monthly report in pdf
        # Create reports directory
        reports_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        # Generate filename
        filename = os.path.join(
            reports_dir,
            f"Monthly_Revenue_Report_{month_name}_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5 * inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1A1054'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1A1054'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        # Title
        title = Paragraph("<b>DENTICARE CLINIC</b>", title_style)
        elements.append(title)

        subtitle = Paragraph(f"<b>Monthly Revenue Report - {month_name} {year}</b>", heading_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3 * inch))

        # Summary Section
        summary_title = Paragraph("<b>REVENUE SUMMARY</b>", heading_style)
        elements.append(summary_title)
        elements.append(Spacer(1, 0.1 * inch))

        total_revenue = total_data['TotalRevenue'] or 0
        transaction_count = total_data['TransactionCount'] or 0

        summary_data = [
            ['Total Revenue:', f"₱{total_revenue:,.2f}"],
            ['Total Transactions:', str(transaction_count)],
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
        ]

        summary_table = Table(summary_data, colWidths=[2.5 * inch, 3 * inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1A1054')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Revenue by Service Section
        service_title = Paragraph("<b>REVENUE BREAKDOWN BY SERVICE</b>", heading_style)
        elements.append(service_title)
        elements.append(Spacer(1, 0.1 * inch))

        service_data = [['Service', 'Quantity', 'Revenue']]
        for service in service_revenue:
            service_data.append([
                service['ServiceName'],
                str(service['TotalQuantity']),
                f"₱{service['TotalRevenue']:,.2f}"
            ])

        service_table = Table(service_data, colWidths=[3 * inch, 1.5 * inch, 2 * inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A1054')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(service_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Transactions Detail Section
        trans_title = Paragraph("<b>TRANSACTION DETAILS</b>", heading_style)
        elements.append(trans_title)
        elements.append(Spacer(1, 0.1 * inch))

        # Build transaction data (smaller font for space)
        trans_data = [['ID', 'Processed By', 'Patient', 'Dentist', 'Service', 'Qty', 'Amount', 'Date']]

        for trans in transactions:
            date_str = trans['TransactionDate'].strftime('%m/%d/%y')
            trans_data.append([
                str(trans['TransactionID']),
                trans['ProcessedBy'][:15] + '...' if len(trans['ProcessedBy']) > 15 else trans['ProcessedBy'],
                trans['PatientName'][:15] + '...' if len(trans['PatientName']) > 15 else trans['PatientName'],
                trans['DentistName'][:15] + '...' if len(trans['DentistName']) > 15 else trans['DentistName'],
                trans['Service'][:12] + '...' if len(trans['Service']) > 12 else trans['Service'],
                str(trans['Quantity']),
                f"₱{trans['TotalAmount']:,.2f}",
                date_str
            ])

        trans_table = Table(trans_data,
                            colWidths=[0.4 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 0.4 * inch, 0.9 * inch,
                                       0.7 * inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A1054')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Qty
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),  # Amount
            ('ALIGN', (7, 1), (7, -1), 'CENTER'),  # Date
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(trans_table)

        # Build PDF
        doc.build(elements)

        return filename

    def exportRecordsTableToPDF(self):
        """Export the current records table to PDF with notes"""
        try:
            # Check if search field exists and has a value
            if not hasattr(self.view, 'searchField'):
                QMessageBox.warning(
                    self.view,
                    "Search Required",
                    "Please search for a patient ID first before exporting records."
                )
                return

            search_value = self.view.searchField.text().strip()

            # Validate that a patient ID has been searched
            if not search_value:
                QMessageBox.warning(
                    self.view,
                    "Search Required",
                    "Please enter a Patient ID in the search field and click search before exporting records."
                )
                return

            # Validate that it's a number (Patient ID)
            if not search_value.isdigit():
                QMessageBox.warning(
                    self.view,
                    "Invalid Patient ID",
                    "Please enter a valid numeric Patient ID in the search field."
                )
                return

            # ✅ GET DATA WITH NOTES from the model
            patient_id = search_value
            records_data = self.transaction_model.getTransactionRecordsForExport(patient_id)

            if not records_data:
                QMessageBox.warning(
                    self.view,
                    "No Data",
                    f"No records found for Patient ID: {patient_id}."
                )
                return

            # Get patient name from first record
            patient_name = records_data[0]['PatientName'] if records_data else 'Unknown Patient'

            # Generate PDF with notes
            filename = self._createRecordsExportPDF(records_data, patient_id, patient_name)

            # Success message with option to open
            msg = QMessageBox(self.view)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Export Successful")
            msg.setText(
                f"Transaction records exported successfully!\n\n"
                f"Patient ID: {patient_id}\n"
                f"Patient Name: {patient_name}\n"
                f"Total Records: {len(records_data)}\n\n"
                f"Report saved as:\n{filename}"
            )

            open_btn = msg.addButton("Open Report", QMessageBox.ButtonRole.ActionRole)
            ok_btn = msg.addButton(QMessageBox.StandardButton.Ok)

            msg.exec()

            # Open report if button clicked
            if msg.clickedButton() == open_btn:
                import subprocess
                import platform

                if platform.system() == 'Windows':
                    os.startfile(filename)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', filename])
                else:  # Linux
                    subprocess.call(['xdg-open', filename])

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Export Error",
                f"Failed to export records: {e}"
            )
            print(f"Export error: {e}")
            import traceback
            traceback.print_exc()

    def _createRecordsExportPDF(self, records_data, patient_id, patient_name):
        """Create PDF export of transaction records with VAT breakdown and notes"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
        from datetime import datetime
        from collections import defaultdict
        import os

        # Create reports directory
        reports_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        # Generate filename
        filename = os.path.join(
            reports_dir,
            f"Patient_Records_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5 * inch,
                                leftMargin=0.5 * inch, rightMargin=0.5 * inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1A1054'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1A1054'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        notes_style = ParagraphStyle(
            'NotesStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            leftIndent=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8
        )

        # Title
        title = Paragraph("<b>DENTICARE CLINIC</b>", title_style)
        elements.append(title)

        subtitle = Paragraph(f"<b>Patient Transaction Records</b>", heading_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.2 * inch))

        # Patient Information Section
        patient_info_title = Paragraph("<b>PATIENT INFORMATION</b>", heading_style)
        elements.append(patient_info_title)
        elements.append(Spacer(1, 0.1 * inch))

        patient_info_data = [
            ['Patient ID:', patient_id],
            ['Patient Name:', patient_name],
            ['Total Transactions:', str(len(set(r['TransactionID'] for r in records_data)))],
            ['Export Date:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
        ]

        patient_info_table = Table(patient_info_data, colWidths=[2 * inch, 4 * inch])
        patient_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1A1054')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(patient_info_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Transaction Records Table
        trans_title = Paragraph("<b>TRANSACTION RECORDS</b>", heading_style)
        elements.append(trans_title)
        elements.append(Spacer(1, 0.1 * inch))

        # Calculate grand totals
        grand_total = 0.0
        grand_base = 0.0
        grand_vat = 0.0

        # Group records by transaction ID
        transactions = defaultdict(list)
        transaction_info = {}

        for record in records_data:
            trans_id = record['TransactionID']
            transactions[trans_id].append(record)

            # Store transaction-level info
            if trans_id not in transaction_info:
                transaction_info[trans_id] = {
                    'ProcessedBy': record['ProcessedBy'],
                    'DentistName': record['DentistName'],
                    'TransactionDate': record['TransactionDate'],
                    'Notes': record.get('Notes')
                }

        # Process each transaction
        for trans_id in sorted(transactions.keys(), reverse=True):
            services = transactions[trans_id]
            info = transaction_info[trans_id]

            # Transaction Header
            trans_header_text = f"<b>Transaction #{trans_id}</b> - {info['TransactionDate'].strftime('%B %d, %Y')}"
            trans_header = Paragraph(trans_header_text, heading_style)
            elements.append(trans_header)
            elements.append(Spacer(1, 0.05 * inch))

            # Transaction Info
            trans_info_data = [
                ['Processed By:', info['ProcessedBy']],
                ['Dentist:', info['DentistName']],
            ]

            trans_info_table = Table(trans_info_data, colWidths=[1.5 * inch, 5 * inch])
            trans_info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(trans_info_table)
            elements.append(Spacer(1, 0.1 * inch))

            # Services table with VAT breakdown
            table_data = [['Service', 'Base Price', 'VAT', 'Price', 'Qty', 'Total']]

            trans_total = 0.0
            trans_base = 0.0
            trans_vat = 0.0

            for record in services:
                base_price = float(str(record.get('BasePrice', 0)).replace('₱', '').replace(',', ''))
                vat_amount = float(str(record.get('VATAmount', 0)).replace('₱', '').replace(',', ''))
                price = float(str(record['PriceAtTransaction']).replace('₱', '').replace(',', ''))
                quantity = record['Quantity']
                total = float(str(record['Total']).replace('₱', '').replace(',', ''))

                trans_base += base_price * quantity
                trans_vat += vat_amount * quantity
                trans_total += total

                # Show VAT only if applicable
                vat_display = f"₱{vat_amount:.2f}" if vat_amount > 0 else "N/A"

                table_data.append([
                    record['Service'][:20] + '...' if len(record['Service']) > 20 else record['Service'],
                    f"₱{base_price:.2f}",
                    vat_display,
                    f"₱{price:.2f}",
                    str(quantity),
                    f"₱{total:.2f}"
                ])

            # Add transaction summary rows
            table_data.append(['', '', '', '', 'Base Total:', f"₱{trans_base:.2f}"])
            table_data.append(['', '', '', '', 'VAT (12%):', f"₱{trans_vat:.2f}"])
            table_data.append(['', '', '', '', 'Subtotal:', f"₱{trans_total:.2f}"])

            grand_base += trans_base
            grand_vat += trans_vat
            grand_total += trans_total

            service_table = Table(table_data,
                                  colWidths=[2 * inch, 0.8 * inch, 0.7 * inch, 0.8 * inch, 0.6 * inch, 0.9 * inch])
            service_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A1054')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

                # Data rows
                ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -4), 7),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 1), (-1, -4), 4),
                ('TOPPADDING', (0, 1), (-1, -4), 4),

                # Summary rows
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -3), (-1, -2), 8),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.grey),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1A1054')),
                ('BOTTOMPADDING', (0, -3), (-1, -1), 4),
                ('TOPPADDING', (0, -3), (-1, -1), 4),
            ]))
            elements.append(service_table)

            # Add notes if present
            if info['Notes']:
                elements.append(Spacer(1, 0.1 * inch))
                notes_label = Paragraph("<b>Notes:</b>", notes_style)
                elements.append(notes_label)

                notes_text = info['Notes'].replace('\n', '<br/>')
                notes_content = Paragraph(notes_text, notes_style)
                elements.append(notes_content)

            elements.append(Spacer(1, 0.2 * inch))

        # Grand Total Section with VAT Breakdown
        elements.append(Spacer(1, 0.1 * inch))

        grand_total_header = Paragraph("<b>SUMMARY</b>", heading_style)
        elements.append(grand_total_header)
        elements.append(Spacer(1, 0.05 * inch))

        grand_summary_data = [
            ['Base Amount:', f"₱{grand_base:.2f}"],
            ['Total VAT (12%):', f"₱{grand_vat:.2f}"],
            ['GRAND TOTAL:', f"₱{grand_total:.2f}"]
        ]

        grand_summary_table = Table(grand_summary_data, colWidths=[5.3 * inch, 1.2 * inch])
        grand_summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 11),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1A1054')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(grand_summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(
            f"DentiCare Clinic - Patient Transaction Records<br/>"
            f"Patient ID: {patient_id} | VAT rate of 12% is already included in prices<br/>"
            f"This is a system-generated report.",
            footer_style
        )
        elements.append(footer)

        # Build PDF
        doc.build(elements)

        return filename