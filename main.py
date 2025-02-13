import tkinter as tk
from cost_calculator import CostCalculatorApp

if __name__ == "__main__":
    app = tk.Tk()
    costCalculatorApp = CostCalculatorApp(app)
    app.mainloop()
