from tkinter import messagebox
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
import os
from datetime import datetime

def export_to_pdf(costs):
    try:
        filename = f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Page 1 - Header and Comparison Chart
        elements.append(Paragraph("Cloud Cost Analysis Report", styles['Title']))
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Cost Summary", styles['Heading2']))

        # Create and save chart image
        fig = create_pdf_figure(costs)
        temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(temp_img.name, bbox_inches='tight')
        plt.close(fig)

        # Add chart to first page
        img = Image(temp_img.name, width=500, height=300)
        elements.append(img)
        elements.append(Spacer(1, 24))

        # Page Break
        from reportlab.platypus import PageBreak
        elements.append(PageBreak())

        # Page 2 - Detailed Cost Breakdown
        elements.append(Paragraph("Cost Breakdown", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # Create breakdown table
        data = create_pdf_table_data(costs)
        table = Table(data, colWidths=[120, 250, 100])
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

        messagebox.showinfo("Export Successful",
                            f"Report saved as:\n{os.path.abspath(filename)}")
    except Exception as e:
        messagebox.showerror("Export Failed", f"Error generating PDF: {str(e)}")

def create_pdf_figure(costs):
    fig = plt.Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    services = ['ECS Fargate', 'Confluent Connector', 'EKS with EC2']
    costs_total = [costs['ECS']['total'], costs['Confluent']['total'], costs['EKS']['total']]
    colors = ['#3498db', '#e67e22', '#2ecc71']

    bars = ax.bar(services, costs_total, color=colors)
    ax.set_title('Cost Summary', fontsize=12)
    ax.set_ylabel('USD ($)', fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'${height:.2f}', ha='center', va='bottom', fontsize=8)
    return fig

def create_pdf_table_data(costs):
    data = [
        ["Service", "Cost Components", "Total"],
        ["ECS Fargate",
         f"Number of Tasks: {costs['ECS']['tasks']}\n"
         f"Task Duration per month (hours): {costs['ECS']['tasks']} x {costs['ECS']['duration']}h\n"
         f"vCPUs per Task: {costs['ECS']['vcpu']}\n"
         f"Memory per Task (GB): {costs['ECS']['memory']}GB\n"
         f"vCPU Cost: ${costs['ECS']['vcpu_cost']:.2f}\n"
         f"Memory Cost: ${costs['ECS']['memory_cost']:.2f}\n"
         f"Throughput (MBps): {costs['ECS']['throughput']}MBps\n"         
         f"Data Transfer Cost: ${costs['ECS']['data_transfer_cost']:.2f}",
         f"${costs['ECS']['total']:.2f}"],

        ["Confluent Connector",
         f"Number of Tasks: {costs['Confluent']['tasks']}\n"
         f"Task Duration per month (hours): {costs['Confluent']['tasks']} x {costs['Confluent']['duration']}h\n"
         f"Connector Task Cost: ${costs['Confluent']['task_cost']:.2f}\n"
         f"Throughput (MBps): {costs['Confluent']['throughput']}MBps\n"
         f"Data Transfer Cost: ${costs['Confluent']['data_transfer_cost']:.2f}",
         f"${costs['Confluent']['total']:.2f}"],

        ["EKS with EC2",
         f"Cluster Cost (per month): ${costs['EKS']['eks_cluster_cost']:.2f}\n"
         f"Number of EC2 Nodes: {costs['EKS']['nodes']}\n"
         f"Node Duration per month (hours): {costs['EKS']['nodes']} x {costs['EKS']['duration']}h\n"
         f"Node Cost: ${costs['EKS']['eks_node_cost']:.2f}\n"
         f"Throughput (MBps): {costs['EKS']['throughput']}MBps\n"
         f"Data Transfer Cost: ${costs['EKS']['data_transfer_cost']:.2f}",
         f"${costs['EKS']['total']:.2f}"]
    ]
    return data