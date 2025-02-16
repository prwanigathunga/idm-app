from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
import os
from datetime import datetime

class ExportReport(ttk.Frame):

    def export_to_pdf(self, costs):
        try:
            # Create PDF document
            filename = f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            elements = []

            # Create temporary figure
            fig = self.create_pdf_figure(costs)
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            fig.savefig(temp_img.name, bbox_inches='tight')
            plt.close(fig)

            # Add content to PDF
            styles = getSampleStyleSheet()

            # Title
            elements.append(Paragraph("Cloud Cost Analysis Report", styles['Title']))
            elements.append(Spacer(1, 24))

            # Cost Comparison Chart
            elements.append(Paragraph("Cost Summary", styles['Heading2']))
            img = Image(temp_img.name, width=400, height=250)
            elements.append(img)
            elements.append(Spacer(1, 24))

            # Detailed Cost Breakdown
            elements.append(Paragraph("Detailed Cost Breakdown", styles['Heading2']))
            data = self.create_pdf_table_data(costs)
            table = Table(data, colWidths=[120, 200, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 24))

            # Generate PDF
            doc.build(elements)
            temp_img.close()
            os.unlink(temp_img.name)

            messagebox.showinfo("Export Successful", f"Report saved as:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error generating PDF: {str(e)}")


    def create_pdf_figure(self, costs):
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        services = ['ECS Fargate', 'Confluent', 'EKS']
        costs_total = [costs['ECS']['total'], costs['Confluent']['total'], costs['EKS']['total']]
        colors = ['#3498db', '#e67e22', '#2ecc71']

        bars = ax.bar(services, costs_total, color=colors)
        ax.set_title('Cost Comparison', fontsize=12)
        ax.set_ylabel('USD ($)', fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=8)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'${height:.2f}', ha='center', va='bottom', fontsize=8)
        return fig


    def create_pdf_table_data(self, costs):
        data = [
            ["Service", "Cost Components", "Total"],
            ["ECS Fargate",
             f"Tasks: {costs['ECS']['tasks']}\n"
             f"vCPU: {costs['ECS']['vcpu']}\n"
             f"Memory: {costs['ECS']['memory']}GB\n"
             f"Duration: {costs['ECS']['duration']}h\n"
             f"Data Transfer: ${costs['ECS']['data_transfer_cost']:.2f}",
             f"${costs['ECS']['total']:.2f}"],

            ["Confluent",
             f"Tasks: {costs['Confluent']['tasks']}\n"
             f"Duration: {costs['Confluent']['duration']}h\n"
             f"Data Transfer: ${costs['Confluent']['data_transfer_cost']:.2f}",
             f"${costs['Confluent']['total']:.2f}"],

            ["EKS",
             f"Cluster Cost: $73.00\n"
             f"Nodes: {costs['EKS']['nodes']}\n"
             f"Duration: {costs['EKS']['duration']}h\n"
             f"Data Transfer: ${costs['EKS']['data_transfer_cost']:.2f}",
             f"${costs['EKS']['total']:.2f}"]
        ]
        return data