import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from export_report import export_to_pdf

class Results(ttk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.load_result_view()

    def load_result_view(self):
        costs = self.controller.calculate_costs()
        results_window = tk.Toplevel(self.controller.root)
        results_window.title("Cost Calculation Results")
        results_window.geometry("1000x700")  # Match main window size
        # results_window.state("zoomed")

        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        comparison_frame = ttk.Frame(notebook)
        self.create_comparison_frame(comparison_frame, costs)
        notebook.add(comparison_frame, text="Cost Summary")

        breakdown_frame = ttk.Frame(notebook)
        self.create_breakdown_frame(breakdown_frame, costs)
        notebook.add(breakdown_frame, text="Cost Breakdown")

        btn_frame = ttk.Frame(results_window)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="🏠 Home", command=lambda: [results_window.destroy(), self.controller.show_home()]).pack(
            side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🔄 New Calculation", command=lambda: [results_window.destroy(), self.controller.start_quiz()]).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="📤 Export PDF", style="Accent.TButton", command=lambda: export_to_pdf(costs)).pack(side=tk.RIGHT, padx=10)

    def create_comparison_frame(self, parent, costs):
        # Create container frame
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        # Chart
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        services = ['ECS Fargate', 'Confluent Connector', 'EKS with EC2']
        costs_total = [
            costs['ECS']['total'],
            costs['Confluent']['total'],
            costs['EKS']['total']
        ]
        colors = ['#3498db', '#e67e22', '#2ecc71']

        bars = ax.bar(services, costs_total, color=colors)
        ax.set_title('Cost Summary', fontsize=14, pad=15)
        ax.set_ylabel('Cost (USD)', fontsize=12)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'${height:.2f}', ha='center', va='bottom', fontsize=11)

        # Add legend
        ax.legend(bars, services)

        chart = FigureCanvasTkAgg(fig, container)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def create_breakdown_frame(self, parent, costs):
        service_notebook = ttk.Notebook(parent)
        service_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ecs_frame = ttk.Frame(service_notebook)
        self.create_service_breakdown(ecs_frame, "ECS Fargate", costs['ECS'])
        service_notebook.add(ecs_frame, text="ECS Fargate")

        confluent_frame = ttk.Frame(service_notebook)
        self.create_service_breakdown(confluent_frame, "Confluent Connector", costs['Confluent'])
        service_notebook.add(confluent_frame, text="Confluent Connector")

        confluent_frame = ttk.Frame(service_notebook)
        self.create_service_breakdown(confluent_frame, "EKS with EC2", costs['EKS'])
        service_notebook.add(confluent_frame, text="EKS with EC2")

    def create_service_breakdown(self, parent, service, data):
        tree = ttk.Treeview(parent, columns=("Parameter", "Value"), show="headings")
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")

        if service == "ECS Fargate":
            items = [
                ("Number of Tasks", data['tasks']),
                ("Task Duration per month (hours)", f"{data['tasks']} x {data['duration']}h"),
                ("vCPUs per Task", data['vcpu']),
                ("Memory per Task (GB)", data['memory']),
                ("vCPU Cost", f"${data['vcpu_cost']:.2f}"),
                ("Memory Cost", f"${data['memory_cost']:.2f}"),
                ("Throughput (MBps)", f"{data['throughput']}MBps"),
                ("Data Transfer Cost", f"${data['data_transfer_cost']:.2f}"),
                ("Total Cost", f"${data['total']:.2f}")
            ]
        elif service == "Confluent Connector":
            items = [
                ("Number of Tasks", data['tasks']),
                ("Task Duration per month (hours)", f"{data['tasks']} x {data['duration']}h"),
                ("Connector Task Cost", f"${data['task_cost']:.2f}"),
                ("Throughput (MBps)", f"{data['throughput']}MBps"),
                ("Data Transfer Cost", f"${data['data_transfer_cost']:.2f}"),
                ("Total Cost", f"${data['total']:.2f}")
            ]
        else:  # EKS
            items = [
                ("Cluster Cost (per month)", f"${data['eks_cluster_cost']:.2f}"),
                ("Number of EC2 Nodes", data['nodes']),
                ("Node Duration per month (hours)", f"{data['nodes']} x {data['duration']}h"),
                ("Node Cost", f"${data['eks_node_cost']:.2f}"),
                ("Throughput (MBps)", f"{data['throughput']}MBps"),
                ("Data Transfer Cost", f"${data['data_transfer_cost']:.2f}"),
                ("Total Cost", f"${data['total']:.2f}")
            ]

        for item in items:
            tree.insert("", tk.END, values=item)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)