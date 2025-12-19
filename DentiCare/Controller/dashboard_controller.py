from DentiCare.Model.dashboard_model import DashboardModel
from PyQt6.QtWidgets import QVBoxLayout, QLabel
import pandas as pd
import calendar


class DashboardTabController:
    def __init__(self, view):
        self.view = view
        self.dashboard_model = DashboardModel()
        self.canvas = None  # Initialize canvas
        self.graph_loaded = False  # Track if graph is already loaded

    def loadDashboardData(self):
        try:
            totalPatients = self.dashboard_model.getTotalPatients()
            totalStaff = self.dashboard_model.getTotalStaff()
            totalRevenue = self.dashboard_model.getTotalRevenue()

            self.view.totalpatientField.setText(str(totalPatients))
            self.view.totalstaffField.setText(str(totalStaff))
            self.view.totalrevenueField.setText(f"₱{totalRevenue:,.2f}")

            print("Dashboard data loaded successfully")

            # Load graph
            self.loadMonthlySalesGraph()

        except Exception as e:
            print(f"Error in loadDashboardData: {e}")
            import traceback
            traceback.print_exc()

    def switchToDashboard(self):
        try:
            self.view.switchToTab(0)

            # Update text fields
            totalPatients = self.dashboard_model.getTotalPatients()
            totalStaff = self.dashboard_model.getTotalStaff()
            totalRevenue = self.dashboard_model.getTotalRevenue()

            self.view.totalpatientField.setText(str(totalPatients))
            self.view.totalstaffField.setText(str(totalStaff))
            self.view.totalrevenueField.setText(f"₱{totalRevenue:,.2f}")

            # FIXED: Always reload the graph to prevent zoom issues
            self.loadMonthlySalesGraph()

        except Exception as e:
            print(f"Error in switchToDashboard: {e}")
            import traceback
            traceback.print_exc()

    def loadMonthlySalesGraph(self):
        """Create and display monthly sales graph in graphFrame using pandas only"""
        try:
            print("Starting to load graph...")

            # Get data from model as DataFrame
            df = self.dashboard_model.getMonthlySalesData()
            print(f"Retrieved data: {len(df)} rows")

            # IMPROVED: Better cleanup of previous canvas
            if self.canvas:
                print("Removing old canvas")
                try:
                    self.canvas.figure.clear()  # Clear the matplotlib figure
                    self.canvas.deleteLater()
                    self.canvas = None
                except:
                    pass

            # Setup layout with proper cleanup
            if self.view.graphFrame.layout():
                layout = self.view.graphFrame.layout()
                # Clear all widgets from layout
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.view.graphFrame)
                layout.setContentsMargins(0, 0, 0, 0)
                self.view.graphFrame.setLayout(layout)

            if not df.empty:
                print("Processing data with pandas...")

                # Process data with pandas
                all_months = pd.DataFrame({'Month': range(1, 13)})
                df = all_months.merge(df, on='Month', how='left')
                df['TotalSales'] = df['TotalSales'].fillna(0)
                df['MonthName'] = df['Month'].apply(lambda x: calendar.month_abbr[x])
                df_plot = df.set_index('MonthName')

                print("Creating plot...")

                try:
                    import matplotlib
                    matplotlib.use('Qt5Agg')
                    import matplotlib.pyplot as plt
                    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                    print("Matplotlib imported successfully")
                except ImportError as e:
                    print(f"Error importing matplotlib: {e}")
                    label = QLabel("Matplotlib not installed. Install with: pip install matplotlib")
                    layout.addWidget(label)
                    return

                # Close any existing matplotlib figures to free memory
                plt.close('all')

                # Use exact frame dimensions
                dpi = 100
                fig_width = 941 / dpi
                fig_height = 361 / dpi

                # Create plot using pandas built-in plotting
                ax = df_plot['TotalSales'].plot(
                    kind='line',
                    figsize=(fig_width, fig_height),
                    color='#1A1054',
                    linewidth=2.5,
                    marker='o',
                    markersize=8,
                    markerfacecolor='#1A1054',
                    markeredgecolor='white',
                    markeredgewidth=2,
                    title='Monthly Sales Overview',
                    xlabel='Month',
                    ylabel='Sales (₱)',
                    grid=True
                )

                print("Plot created")

                fig = ax.get_figure()
                fig.patch.set_facecolor('#f0f0f0')
                ax.set_facecolor('#ffffff')

                # Add value labels
                for i, value in enumerate(df_plot['TotalSales']):
                    if value > 0:
                        ax.text(i, value, f'₱{value:,.0f}',
                                ha='center', va='bottom', fontsize=9,
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

                # Style the plot
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₱{x:,.0f}'))
                ax.grid(axis='both', alpha=0.3, linestyle='--')
                ax.set_title('Monthly Sales Overview', fontsize=12, fontweight='bold', pad=15)
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

                # Calculate total sales only
                total_sales = df['TotalSales'].sum()

                # Add statistics text (only total)
                stats_text = f"Total Sales: ₱{total_sales:,.0f}"
                fig.text(0.5, 0.02, stats_text, ha='center', fontsize=9,
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

                fig.tight_layout()

                print("Adding canvas to layout...")

                # Create fresh canvas
                self.canvas = FigureCanvas(fig)
                self.canvas.setFixedSize(941, 361)
                layout.addWidget(self.canvas)
                self.canvas.draw()

                print("Graph loaded successfully!")

            else:
                print("No sales data available for graph")
                label = QLabel("No sales data available")
                label.setStyleSheet("font-size: 14px; color: #666;")
                layout.addWidget(label)

        except Exception as e:
            print(f"ERROR in loadMonthlySalesGraph: {e}")
            import traceback
            traceback.print_exc()

            # Try to show error message in the frame
            try:
                if self.view.graphFrame.layout():
                    layout = self.view.graphFrame.layout()
                else:
                    layout = QVBoxLayout(self.view.graphFrame)
                    self.view.graphFrame.setLayout(layout)

                error_label = QLabel(f"Error loading graph: {str(e)}")
                error_label.setStyleSheet("color: red; font-size: 12px;")
                layout.addWidget(error_label)
            except:
                pass