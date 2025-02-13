import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        notebook.add(comparison_frame, text="Cost Comparison")

        breakdown_frame = ttk.Frame(notebook)
        self.create_breakdown_frame(breakdown_frame, costs)
        notebook.add(breakdown_frame, text="Detailed Cost")

        btn_frame = ttk.Frame(results_window)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="🏠 Home", command=lambda: [results_window.destroy(), self.controller.show_home()]).pack(
            side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🔄 New Calculation", command=lambda: [results_window.destroy(), self.controller.start_quiz()]).pack(side=tk.LEFT, padx=10)

    def create_comparison_frame(self, parent, costs):
        # Create container frame
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        # label = ttk.Label(container, text="Cost Summary", font=("Arial", 12, "bold"))
        # label.pack(pady=(10, 5))  # Add padding for spacing
        # # Create summary table
        # summary_table = ttk.Treeview(container, columns=("Service", "Total Cost", "Compute/Tasks", "Data Transfer"),
        #                              show="headings", height=2)
        #
        # # Configure columns
        # summary_table.heading("Service", text="Service")
        # summary_table.heading("Total Cost", text="Total Cost")
        # summary_table.heading("Compute/Tasks", text="Compute/Tasks Cost")
        # summary_table.heading("Data Transfer", text="Data Transfer Cost")
        #
        # summary_table.column("Service", width=150, anchor=tk.W)
        # summary_table.column("Total Cost", width=120, anchor=tk.E)
        # summary_table.column("Compute/Tasks", width=150, anchor=tk.E)
        # summary_table.column("Data Transfer", width=150, anchor=tk.E)
        #
        # # Add data rows
        # summary_table.insert("", tk.END, values=(
        #     "ECS Fargate",
        #     f"${costs['ECS']['total']:.2f}",
        #     f"${costs['ECS']['vcpu_cost'] + costs['ECS']['memory_cost']:.2f}",
        #     f"${costs['ECS']['data_transfer_cost']:.2f}"
        # ))
        #
        # summary_table.insert("", tk.END, values=(
        #     "Confluent Managed",
        #     f"${costs['Confluent']['total']:.2f}",
        #     f"${costs['Confluent']['task_cost']:.2f}",
        #     f"${costs['Confluent']['data_cost']:.2f}"
        # ))
        #
        # # Style the table
        # style = ttk.Style()
        # style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        # style.configure("Treeview", font=("Arial", 10), rowheight=25)
        #
        # summary_table.pack(fill=tk.X, pady=(0, 20))

        # Chart
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        services = ['ECS Fargate', 'Confluent Managed']
        costs_total = [costs['ECS']['total'], costs['Confluent']['total']]
        colors = ['#3498db', '#e67e22']

        bars = ax.bar(services, costs_total, color=colors)
        ax.set_title('Cost Comparison', fontsize=14, pad=15)
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
        self.create_service_breakdown(confluent_frame, "Confluent Managed", costs['Confluent'])
        service_notebook.add(confluent_frame, text="Confluent Managed")

    def create_service_breakdown(self, parent, service, data):
        tree = ttk.Treeview(parent, columns=("Parameter", "Value"), show="headings")
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")

        if service == "ECS Fargate":
            items = [
                ("Number of Tasks", data['tasks']),
                ("vCPUs per Task", data['vcpu']),
                ("Memory per Task (GB)", data['memory']),
                ("vCPU Cost", f"${data['vcpu_cost']:.2f}"), ("Memory Cost", f"${data['memory_cost']:.2f}"),
                ("Data Transfer Cost", f"${data['data_transfer_cost']:.2f}"), ("Total Cost", f"${data['total']:.2f}")
            ]
        else:
            items = [
                ("Number of Tasks", data['tasks']),
                ("Task Duration (hours)", data['duration']),
                ("Connector Cost", f"${data['task_cost']:.2f}"), ("Data Transfer Cost", f"${data['data_cost']:.2f}"),
                ("Total Cost", f"${data['total']:.2f}")
            ]

        for item in items:
            tree.insert("", tk.END, values=item)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)