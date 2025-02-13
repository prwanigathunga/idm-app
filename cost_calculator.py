import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from PIL import Image, ImageTk

from results import Results


class CostCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud Cost Calculator")
        self.root.geometry("1000x700")

        # Initialize data and UI states
        self.questions = None
        self.answers = None
        self.logic = None
        self.pricing = None
        self.user_responses = {}
        self.current_question = 0

        # Configure styles
        self.setup_styles()
        self.load_data()

        # Load and resize the image
        img = Image.open("assets/image.png")  # Replace with your image path
        img = img.resize((50, 50), Image.LANCZOS)  # Adjust size as needed
        self.start_img = ImageTk.PhotoImage(img)

        self.create_menu()  # Add menu bar

        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.show_home()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12), padding=10)
        self.style.configure("TButton", font=("Arial", 12), padding=10)  # Increased font size
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        # self.style.configure("Accent.TButton", foreground="#ffffff", background="#2c3e50")
        # self.style.configure("Accent.TButton", font=("Arial", 12, "bold"), foreground="black", padding=(10, 5), background="#4CAF50")

    def load_data(self):
        try:
            self.questions = pd.read_excel("assets/cloud_costs.xlsx", sheet_name="Questions")
            self.answers = pd.read_excel("assets/cloud_costs.xlsx", sheet_name="Answers")
            self.logic = pd.read_excel("assets/cloud_costs.xlsx", sheet_name="Logic")
            self.pricing = pd.read_excel("assets/cloud_costs.xlsx", sheet_name="Pricing").set_index('Parameter')['Value (USD)']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.root.destroy()

    def create_menu(self):
        """Create a menu bar with File and Help options."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Home", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def open_file(self):
        self.show_home()

    def show_about(self):
        messagebox.showinfo("About", "Cloud Cost Calculator\nVersion 1.0\nCreated with Tkinter")

    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.main_frame, text="Cloud Cost Calculator", style="Title.TLabel").pack(pady=40)
        self.start_button = ttk.Button(self.main_frame, text=" Start Calculation", image=self.start_img, compound="left",  # Image on the left side
                                       style="Accent.TButton",
                                       command=self.start_quiz)
        self.start_button.pack(pady=20, ipadx=20, ipady=15)

    def start_quiz(self):
        self.current_question = 0
        self.user_responses = {}
        self.show_question()

    def show_question(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        q_data = self.questions.iloc[self.current_question]
        q_text = q_data['Question Text']
        q_id = q_data['Question ID']
        input_type = q_data['Input Type']

        ttk.Label(self.main_frame, text=f"Question {self.current_question + 1} of {len(self.questions)}",
                  style="Title.TLabel").pack(pady=(20, 40))

        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=50)
        ttk.Label(container, text=q_text, wraplength=600).pack(anchor=tk.W, pady=(0, 20))

        if input_type == 'Multiple Choice':
            self.show_radio_buttons(container, q_id)
        else:
            self.show_numeric_input(container, q_id)

        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(pady=20)

        if self.current_question > 0:
            ttk.Button(nav_frame, text="◀ Back", command=self.prev_question).pack(side=tk.LEFT, padx=10)

        if self.current_question < len(self.questions) - 1:
            ttk.Button(nav_frame, text="Next ▶", command=self.next_question).pack(side=tk.RIGHT, padx=10)
        else:
            ttk.Button(nav_frame, text="📊 Calculate Costs", style="Accent.TButton",
                       command=self.show_results).pack(side=tk.RIGHT, padx=10)

    def show_radio_buttons(self, parent, q_id):
        answers = self.answers[self.answers['Question ID'] == q_id]
        self.var = tk.IntVar()

        for idx, row in answers.iterrows():
            rb = ttk.Radiobutton(parent, text=row['Answer Text'], variable=self.var, value=row['Answer ID'])
            rb.pack(anchor=tk.W, pady=5)
            if self.user_responses.get(q_id) == row['Answer ID']:
                rb.invoke()

    def show_numeric_input(self, parent, q_id):
        self.var = tk.StringVar()
        if q_id in self.user_responses:
            self.var.set(self.user_responses[q_id])
        entry = ttk.Entry(parent, textvariable=self.var, width=15, font=("Arial", 12))
        entry.pack(anchor=tk.W)
        entry.focus()

    def save_response(self):
        q_id = self.questions.iloc[self.current_question]['Question ID']
        if self.questions.iloc[self.current_question]['Input Type'] == 'Multiple Choice':
            self.user_responses[q_id] = self.var.get()
        else:
            try:
                self.user_responses[q_id] = float(self.var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")
                return False
        return True

    def next_question(self):
        if not self.save_response():
            return
        self.current_question += 1
        self.show_question()

    def prev_question(self):
        self.save_response()
        self.current_question -= 1
        self.show_question()

    def calculate_costs(self):
        ecs_tasks = 0
        ecs_vcpu = 0
        ecs_memory = 0
        connector_tasks = 1  # Always at least 1 connector
        data_transfer_multiplier = 1.0

        for q_id, answer_id in self.user_responses.items():
            if isinstance(answer_id, float):
                continue

            logic_row = self.logic[(self.logic['Question ID'] == q_id) & (self.logic['Answer ID'] == answer_id)]

            if not logic_row.empty:
                logic = logic_row.iloc[0]
                ecs_tasks = max(ecs_tasks, logic['ECS Tasks'])
                ecs_vcpu = max(ecs_vcpu, logic['ECS vCPU'])
                ecs_memory = max(ecs_memory, logic['ECS Memory (GB)'])
                connector_tasks = max(connector_tasks, logic['Connector Tasks'])
                data_transfer_multiplier *= logic['Data Transfer Multiplier']

        duration = self.user_responses.get(4, 0)
        throughput = self.user_responses.get(2, 0)
        data_transfer_gb = ((throughput*3600)/1024) * duration * data_transfer_multiplier

        # ECS Calculations
        ecs_vcpu_cost = ecs_tasks * ecs_vcpu * duration * self.pricing['ECS vCPU Cost per hour']
        ecs_memory_cost = ecs_tasks * ecs_memory * duration * self.pricing['ECS Memory Cost per GB-hour']
        ecs_data_transfer_cost = data_transfer_gb * self.pricing['ECS Data Transfer Cost per GB']
        total_ecs = ecs_vcpu_cost + ecs_memory_cost + ecs_data_transfer_cost

        # Connector Calculations
        confluent_task_cost = duration * self.pricing['Confluent Cost per task/hour'] * connector_tasks
        data_transfer_cost = data_transfer_gb * self.pricing['Confluent Data Transfer Cost per GB']
        total_confluent = confluent_task_cost + data_transfer_cost

        return {
            'ECS': {
                'tasks': ecs_tasks, 'vcpu': ecs_vcpu, 'memory': ecs_memory,
                'duration': duration, 'vcpu_cost': ecs_vcpu_cost,
                'memory_cost': ecs_memory_cost, 'data_transfer_cost': ecs_data_transfer_cost,
                'total': total_ecs
            },
            'Confluent': {
                'tasks': connector_tasks, 'duration': duration, 'throughput': throughput,
                'task_cost': confluent_task_cost, 'data_transfer': data_transfer_gb,
                'data_cost': data_transfer_cost, 'total': total_confluent
            }
        }

    def show_results(self):
        if not self.save_response():
            return
        self.resutls_view = Results(self.main_frame, self)
        self.show_results_view()

    def show_results_view(self):
        self.resutls_view.pack_forget()
        self.resutls_view.pack(fill="both", expand=True)