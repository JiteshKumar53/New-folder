import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
import os
from datetime import datetime
from ttkbootstrap import Style
from reportlab.lib import colors
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Mortgage Calculation Engine (Business Logic)
class MortgageCalculatorEngine:
    def __init__(self):
        self.loan_amount: float = 0.0
        self.interest_rate: float = 0.0
        self.term_years: int = 30
        self.extra_payment: float = 0.0
        self.monthly_fee: float = 0.0

    def calculate_amortization(self) -> dict:
        """Calculate full amortization schedule with optional extra payments"""
        monthly_rate = self.interest_rate / 100 / 12
        months = self.term_years * 12
        payment = self.calculate_monthly_payment(monthly_rate, months)
        
        schedule = []
        balance = self.loan_amount
        total_interest = 0.0
        
        for month in range(1, months + 1):
            if balance <= 0:
                break
                
            interest = balance * monthly_rate
            principal = payment - interest
            total_payment = principal + self.extra_payment
            
            if total_payment > balance:
                total_payment = balance
                self.extra_payment = 0
                
            balance -= total_payment
            total_interest += interest
            
            schedule.append({
                'month': month,
                'payment': total_payment + self.monthly_fee,
                'principal': principal,
                'interest': interest,
                'balance': balance,
                'extra_payment': self.extra_payment,
                'fee': self.monthly_fee
            })
            
        return {
            'schedule': schedule,
            'total_interest': total_interest,
            'final_payment_month': len(schedule)
        }

    def calculate_monthly_payment(self, monthly_rate: float, months: int) -> float:
        """Calculate base monthly payment using standard formula"""
        if monthly_rate == 0:
            return self.loan_amount / months
        return (self.loan_amount * monthly_rate * (1 + monthly_rate)**months) / \
               ((1 + monthly_rate)**months - 1)

# Main Application Class (GUI Layer)
class MortgageCalculator:
    def __init__(self, root: tk.Tk):
        """Initialize the calculator"""
        # Initialize tooltips dictionary first
        self.tooltips = {}
        
        self.root = root
        self.root.title("Modern Mortgage Calculator")

        # Bind keyboard shortcuts
        self.root.bind('<Control-Return>', lambda e: self.calculate())
        self.root.bind('<Control-c>', lambda e: self.clear_fields())
        self.root.bind('<Control-e>', lambda e: self.export_pdf())
        self.root.bind('<Escape>', lambda e: self.root.quit())

        # Configure Tailwind-inspired theme
        self.style = Style(theme='litera')
        self.style.configure('.', font=('Inter', 11))
        
        # Extended Tailwind CSS color palette
        self.colors = {
            'zinc-50': '#fafafa',
            'zinc-100': '#f4f4f5', 
            'zinc-200': '#e4e4e7',
            'zinc-400': '#a1a1aa',
            'zinc-600': '#52525b',
            'zinc-800': '#18181b',  # Darker zinc-800 for better contrast
            'emerald-500': '#10b981',
            'emerald-600': '#059669',
            'emerald-700': '#047857',
            'sky-500': '#0ea5e9', 
            'sky-600': '#0284c7',   # Added sky-600 for secondary elements
            'sky-700': '#0369a1',
            'stone-200': '#e7e5e4'
        }

        # Configure widget styles
        self.style.configure('TFrame', background=self.colors['zinc-50'])
        self.style.configure('TLabel', background=self.colors['zinc-50'], 
                           foreground=self.colors['zinc-800'], padding=4)
        self.style.configure('TButton', padding=8, relief='flat')
        self.style.configure('Primary.TButton', background=self.colors['sky-600'],
                           foreground='white', font=('Inter', 11, 'bold'))
        self.style.map('TButton',
                      background=[('active', self.colors['sky-600']), 
                                 ('disabled', self.colors['zinc-100'])],
                      foreground=[('active', 'white'), ('disabled', self.colors['zinc-800'])])

        # Set window size for 14" laptop screen
        self.root.geometry("1200x800")
        self.center_window()

        # Create main container with Tailwind spacing
        main_frame = ttk.Frame(self.root, padding=24)
        main_frame.pack(fill='both', expand=True)

        # Create top frame for columns
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='both', expand=True)

        # Create columns with 1:2 ratio
        left_frame = ttk.Frame(top_frame, width=400)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=8)

        right_frame = ttk.Frame(top_frame, width=800)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=8)

        # Configure column weights (1:2 ratio)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=2)

        # Create bottom frame for visualization
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill='both', expand=True, pady=10)

        # Initialize variables and create panels
        self.initialize_variables()
        self.create_panels(left_frame, right_frame, bottom_frame)
        
        # Create tooltips dictionary to store tooltip instances
        self.tooltips = {}

    def create_tooltip(self, widget, text):
        """Create a tooltip for a given widget with the given text"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Create a toplevel window
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # Create tooltip label
            label = ttk.Label(tooltip, text=text, justify='left',
                            background=self.colors['zinc-50'],
                            relief='solid', borderwidth=1,
                            font=("Inter", 8),
                            padding=(5, 2))
            label.pack()
            
            # Store the tooltip
            self.tooltips[widget] = tooltip
            
        def leave(event):
            # Destroy the tooltip if it exists
            if widget in self.tooltips:
                self.tooltips[widget].destroy()
                del self.tooltips[widget]
                
        # Bind the tooltip to the widget
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def create_panels(self, left_frame, right_frame, bottom_frame):
        """Create all panels in the calculator"""
        # Left column panels
        self.create_currency_panel(left_frame)
        self.create_loan_details_panel(left_frame)
        self.create_calculate_panel(left_frame)

        # Right column panels
        self.create_results_panel(right_frame)

        # Bottom visualization panel
        self.create_visualization_panel(bottom_frame)

    def center_window(self):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.root.geometry(f"+{x}+{y}")

    # STEP 3: Input Fields Creation
    def create_currency_panel(self, parent):
        """Create currency selection panel"""
        currency_frame = ttk.LabelFrame(parent, text="Currency", padding=11)
        currency_frame.pack(fill='x', pady=6)

        # Define currencies with their symbols
        currencies = [
            ("SEK (kr)", "kr"),
            ("USD ($)", "$"),
            ("EUR (€)", "€"),
            ("CAD (C$)", "C$"),
            ("AUD (A$)", "A$"),
            ("INR (₹)", "₹"),
            ("JPY (¥)", "¥"),
            ("GBP (£)", "£")
        ]

        # Create and pack the label with Tailwind-inspired styling
        ttk.Label(currency_frame, text="Select Currency:", 
                font=('Inter', 9),
                padding=(0, 0, 6, 0)).pack(side='left')

        # Create the dropdown menu with tooltip
        currency_menu = ttk.Combobox(
            currency_frame,
            textvariable=self.currency_var,
            values=[curr[1] for curr in currencies],
            state='readonly',
            width=8
        )
        self.create_tooltip(currency_menu, "Select your preferred currency")
        currency_menu.pack(side='left', padx=5)

        # Set the default value
        currency_menu.set("kr")

        # Add a label to show the full currency name
        currency_label = ttk.Label(currency_frame, textvariable=self.currency_name_var)
        currency_label.pack(side='left', padx=5)

        # Create a dictionary for currency names
        self.currency_names = {
            "kr": "Swedish Krona (SEK)",
            "$": "US Dollar (USD)",
            "€": "Euro (EUR)",
            "C$": "Canadian Dollar (CAD)",
            "A$": "Australian Dollar (AUD)",
            "₹": "Indian Rupee (INR)",
            "¥": "Japanese Yen (JPY)",
            "£": "British Pound (GBP)"
        }

        # Bind the selection event to update the currency name
        def update_currency_name(event):
            selected_symbol = self.currency_var.get()
            self.currency_name_var.set(self.currency_names.get(selected_symbol, ""))

        currency_menu.bind('<<ComboboxSelected>>', update_currency_name)

    def create_loan_details_panel(self, parent):
        """Create loan details panel"""
        # Loan Details with card styling
        loan_frame = ttk.LabelFrame(parent, text="Step 2: Enter Loan Details", 
                                  padding=(16, 11), 
                                  style='Card.TLabelframe')
        loan_frame.pack(fill='x', padx=6, pady=6)

        # Configure grid layout with Tailwind spacing
        loan_frame.grid_columnconfigure(0, weight=1, minsize=120)
        loan_frame.grid_columnconfigure(1, weight=3, minsize=220)

        # Loan Seeking - Full width
        loan_seeking_frame = ttk.Frame(loan_frame, padding=4)
        loan_seeking_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        ttk.Label(loan_seeking_frame, text="Loan Seeking For:", 
                 font=('Inter', 9)).pack(side='left')
        self.loan_seeking_entry = ttk.Entry(loan_seeking_frame, textvariable=self.loan_seeking_var, width=24)
        self.create_tooltip(self.loan_seeking_entry, "Enter the total amount you wish to borrow")
        self.loan_seeking_entry.pack(side='right', fill='x', expand=True)
        # Bind the loan seeking entry to update when value changes
        self.loan_seeking_var.trace_add('write', self.update_on_loan_seeking_change)

        # Down Payment - Row 1
        down_payment_frame = ttk.Frame(loan_frame, padding=3)
        down_payment_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        ttk.Label(down_payment_frame, text="Down Payment:", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))

        # Mode Selection
        mode_frame = ttk.Frame(down_payment_frame)
        mode_frame.pack(side='left', fill='x', expand=True)
        
        self.down_payment_mode = tk.StringVar(value="auto")
        ttk.Radiobutton(mode_frame, text="Auto (15%)", variable=self.down_payment_mode, 
                       value="auto", command=self.toggle_down_payment_mode).pack(side='left', padx=2)
        ttk.Radiobutton(mode_frame, text="Manual", variable=self.down_payment_mode,
                       value="manual", command=self.toggle_down_payment_mode).pack(side='left', padx=2)

        # Entry Field
        self.down_payment_entry = ttk.Entry(down_payment_frame, textvariable=self.down_payment_var, width=18)
        self.down_payment_entry.pack(side='right', fill='x', expand=True)
        self.down_payment_entry.configure(state='disabled')

        # Bind the down payment entry to update loan amount when value changes
        self.down_payment_var.trace_add('write', self.update_loan_amount)

        # Loan Amount Display - Row 2
        loan_amount_frame = ttk.Frame(loan_frame, padding=3)
        loan_amount_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        ttk.Label(loan_amount_frame, text="Loan Amount:", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))
        ttk.Entry(loan_amount_frame, textvariable=self.loan_amount_var, state='readonly', width=24).pack(side='right')

        # Interest Rate - Row 3
        interest_frame = ttk.Frame(loan_frame, padding=3)
        interest_frame.grid(row=3, column=0, columnspan=2, sticky='ew')
        ttk.Label(interest_frame, text="Interest Rate (%):", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))
        self.interest_rate_entry = ttk.Entry(interest_frame, textvariable=self.interest_rate_var, width=24)
        self.interest_rate_entry.pack(side='right')

        # Principal Payment - Row 4
        principal_frame = ttk.Frame(loan_frame, padding=3)
        principal_frame.grid(row=4, column=0, columnspan=2, sticky='ew')
        ttk.Label(principal_frame, text="Principal Payment:", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))
        self.principal_payment_entry = ttk.Entry(principal_frame, textvariable=self.principal_payment_var, width=24)
        self.create_tooltip(self.principal_payment_entry, "Enter your planned monthly principal payment")
        self.principal_payment_entry.pack(side='right')

        # Extra Payment - Row 5
        extra_frame = ttk.Frame(loan_frame, padding=3)
        extra_frame.grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Label(extra_frame, text="Extra Payment:", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))
        self.extra_payment_entry = ttk.Entry(extra_frame, textvariable=self.extra_payment_var, width=24)
        self.create_tooltip(self.extra_payment_entry, "Optional: Enter additional monthly payment to reduce loan term")
        self.extra_payment_entry.pack(side='right')

        # Monthly House Fee - Row 6
        fee_frame = ttk.Frame(loan_frame, padding=3)
        fee_frame.grid(row=6, column=0, columnspan=2, sticky='ew')
        ttk.Label(fee_frame, text="Monthly House Fee:", font=('Helvetica', 8)).pack(side='left', padx=(0, 8))
        self.monthly_fee_entry = ttk.Entry(fee_frame, textvariable=self.monthly_fee_var, width=24)
        self.create_tooltip(self.monthly_fee_entry, "Enter monthly maintenance/association fees if applicable")
        self.monthly_fee_entry.pack(side='right')

    def create_calculate_panel(self, parent):
        """Create calculate panel"""
        button_frame = ttk.LabelFrame(parent, text="Step 3: Calculate and Export", 
                                    padding=(16, 11))
        button_frame.pack(fill='x', padx=6, pady=6)

        # Configure grid layout for button alignment
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        # Calculate button
        calc_btn = ttk.Button(button_frame, text="Calculate", 
                             command=self.calculate,
                             style='Primary.TButton',
                             padding=(12, 6))
        calc_btn.grid(row=0, column=0, padx=3, sticky='ew')

        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear", 
                             command=self.clear_fields,
                             padding=(12, 6))
        clear_btn.grid(row=0, column=1, padx=3, sticky='ew')

        # Export PDF button
        export_btn = ttk.Button(button_frame, text="Export PDF", 
                              command=self.export_pdf,
                              padding=(12, 6))
        export_btn.grid(row=0, column=2, padx=3, sticky='ew')

        # Add consistent min width to buttons and tooltips
        calc_btn_text = "Calculate (Ctrl+Enter)"
        clear_btn_text = "Clear (Ctrl+C)"
        export_btn_text = "Export PDF (Ctrl+E)"
        
        calc_btn.configure(width=len(calc_btn_text), text=calc_btn_text)
        clear_btn.configure(width=len(clear_btn_text), text=clear_btn_text)
        export_btn.configure(width=len(export_btn_text), text=export_btn_text)
        
        self.create_tooltip(calc_btn, "Calculate mortgage payments")
        self.create_tooltip(clear_btn, "Clear all fields")
        self.create_tooltip(export_btn, "Export results to PDF")

    # STEP 4: Results Panel Creation
    def create_results_panel(self, parent):
        """Create the results display panel"""
        # Main results container
        results_frame = ttk.LabelFrame(parent, text="Step 4: View Results", 
                                     padding=(14, 11),
                                     style='Card.TLabelframe')
        results_frame.pack(fill='both', expand=True, padx=6, pady=6)

        # Configure grid layout
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(1, weight=1)

        # Key Metrics - Grid layout
        ttk.Label(results_frame, text="Monthly Payment:", 
                 font=('Inter', 8, 'bold'), 
                 foreground=self.colors['zinc-800'],
                 padding=(0, 0, 6, 0)).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Label(results_frame, textvariable=self.monthly_payment_var,
                 font=('Inter', 8), 
                 foreground=self.colors['sky-600'],
                 anchor='e').grid(row=0, column=1, sticky='e', pady=2)

        ttk.Label(results_frame, text="Total Interest:", 
                 font=('Inter', 8, 'bold'),
                 foreground=self.colors['zinc-800'],
                 padding=(0, 0, 6, 0)).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Label(results_frame, textvariable=self.total_interest_var,
                 font=('Inter', 8),
                 foreground=self.colors['sky-600'],
                 anchor='e').grid(row=1, column=1, sticky='e', pady=2)

        # Payment Breakdown Card
        breakdown_frame = ttk.LabelFrame(results_frame, 
                                       text="Monthly Payment Breakdown",
                                       padding=(12, 8),
                                       style='Card.TLabelframe')
        breakdown_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=4)

        # Configure breakdown grid
        breakdown_frame.grid_columnconfigure(0, weight=3)
        breakdown_frame.grid_columnconfigure(1, weight=2)

        breakdown_items = [
            ("Principal Payment:", self.monthly_principal_var),
            ("Extra Payment:", self.monthly_extra_var),
            ("Total Principal:", self.monthly_total_principal_var),
            ("Interest Payment:", self.monthly_interest_var),
            ("Monthly House Fee:", self.monthly_fee_var),
            ("Total Monthly Payment:", self.monthly_total_var)
        ]

        for i, (label, var) in enumerate(breakdown_items):
            ttk.Label(breakdown_frame, text=label, 
                     font=('Inter', 8),
                     foreground=self.colors['zinc-600'],
                     padding=(0, 0, 6, 0)).grid(row=i, column=0, sticky='w', pady=1)
            ttk.Label(breakdown_frame, textvariable=var,
                     font=('Inter', 8),
                     foreground=self.colors['zinc-800'],
                     anchor='e').grid(row=i, column=1, sticky='e', pady=1)

        # Savings Impact Card
        savings_frame = ttk.LabelFrame(results_frame, 
                                     text="With Extra Payments",
                                     padding=(12, 8),
                                     style='Card.TLabelframe')
        savings_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=4)

        # Configure savings grid
        savings_frame.grid_columnconfigure(0, weight=3)
        savings_frame.grid_columnconfigure(1, weight=2)

        savings_items = [
            ("Time Saved:", self.time_saved_var),
            ("Interest Saved:", self.interest_saved_var),
            ("Loan Payoff Time:", self.loan_payoff_time_var)
        ]

        for i, (label, var) in enumerate(savings_items):
            ttk.Label(savings_frame, text=label, 
                     font=('Inter', 8),
                     foreground=self.colors['emerald-700'],
                     padding=(0, 0, 6, 0)).grid(row=i, column=0, sticky='w', pady=1)
            ttk.Label(savings_frame, textvariable=var,
                     font=('Inter', 8, 'bold'),
                     foreground=self.colors['emerald-600'],
                     anchor='e').grid(row=i, column=1, sticky='e', pady=1)

    def create_visualization_panel(self, parent):
        """Create the visualization panel"""
        visualization_frame = ttk.LabelFrame(parent, text="Yearly Payment Breakdown", padding=10, style='Card.TLabelframe')
        visualization_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create container for plot with 6" height (576px at 96dpi)
        self.plot_container = ttk.Frame(visualization_frame, width=30, height=576)
        self.plot_container.pack(fill='both', expand=True)
        
        # Initialize matplotlib components
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_container)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # STEP 5: Input Validation
    def validate_inputs(self):
        """Validate all input fields"""
        try:
            # Validate loan seeking amount with realistic limits
            loan_seeking = self.get_float_value(self.loan_seeking_var.get())
            if loan_seeking <= 0:
                messagebox.showerror("Error", "Loan seeking amount must be greater than 0")
                return False
            if loan_seeking > 100000000:  # 100 million limit
                messagebox.showerror("Error", "Loan seeking amount exceeds maximum limit (100 million)")
                return False

            # Validate down payment
            down_payment = self.get_float_value(self.down_payment_var.get())
            if down_payment < 0:
                messagebox.showerror("Error", "Down payment cannot be negative")
                return False
            if down_payment >= loan_seeking:
                messagebox.showerror("Error", "Down payment must be less than loan seeking amount")
                return False

            # Validate interest rate with realistic limits
            interest_rate = self.get_float_value(self.interest_rate_var.get())
            if interest_rate <= 0:
                messagebox.showerror("Error", "Interest rate must be greater than 0")
                return False
            if interest_rate > 30:  # More realistic maximum interest rate
                messagebox.showerror("Error", "Interest rate seems unusually high (max 30%)")
                return False

            # Validate principal payment
            principal_payment = self.get_float_value(self.principal_payment_var.get())
            if principal_payment < 0:
                messagebox.showerror("Error", "Principal payment cannot be negative")
                return False

            # Validate extra payment
            extra_payment = self.get_float_value(self.extra_payment_var.get())
            if extra_payment < 0:
                messagebox.showerror("Error", "Extra payment cannot be negative")
                return False

            # Validate monthly fee
            monthly_fee = self.get_float_value(self.monthly_fee_var.get())
            if monthly_fee < 0:
                messagebox.showerror("Error", "Monthly house fee cannot be negative")
                return False

            return True

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return False

    # STEP 6: Calculation Logic
    def calculate(self):
        """Calculate mortgage payments and update display"""
        if not self.validate_inputs():
            return

        try:
            # Get and validate values from inputs
            loan_seeking = self.get_float_value(self.loan_seeking_var.get())
            
            # Calculate or get down payment based on mode
            if self.down_payment_mode.get() == "auto":
                # Calculate 15% down payment
                down_payment = loan_seeking * 0.15
                self.down_payment_var.set(f"{down_payment:,.0f}")
            else:
                down_payment = self.get_float_value(self.down_payment_var.get())
            
            # Validate down payment
            if down_payment >= loan_seeking:
                messagebox.showerror("Error", "Down payment cannot be greater than or equal to loan seeking amount")
                return False
            
            # Calculate loan amount by subtracting down payment
            loan_amount = loan_seeking - down_payment
            # Update the loan amount display
            self.loan_amount_var.set(f"{loan_amount:,.0f}")
            
            # Store these values immediately for later use
            self.current_values['loan_seeking'] = float(loan_seeking)
            self.current_values['down_payment'] = float(down_payment)
            self.current_values['loan_amount'] = float(loan_amount)
            interest_rate = self.get_float_value(self.interest_rate_var.get())
            principal_payment = self.get_float_value(self.principal_payment_var.get())
            extra_payment = self.get_float_value(self.extra_payment_var.get() or "0")
            monthly_fee = self.get_float_value(self.monthly_fee_var.get())

            # Calculate monthly rate and base payment
            monthly_rate = interest_rate / 100 / 12
            base_monthly = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -360)

            # Calculate monthly interest
            monthly_interest = loan_amount * monthly_rate

            # Calculate total monthly payment
            total_monthly = principal_payment + extra_payment + monthly_interest + monthly_fee

            # Calculate total interest over loan term
            total_interest = (base_monthly * 360) - loan_amount

            # Calculate payoff times
            if extra_payment > 0:
                total_monthly_payment = principal_payment + extra_payment
                months_with_extra = int(loan_amount / total_monthly_payment)
                
                # Calculate interest savings
                total_interest_with_extra = 0
                remaining_balance = loan_amount
                for _ in range(months_with_extra):
                    interest = remaining_balance * monthly_rate
                    total_interest_with_extra += interest
                    remaining_balance -= total_monthly_payment
                
                interest_saved = total_interest - total_interest_with_extra
                years_to_payoff = months_with_extra // 12
                months_to_payoff = months_with_extra % 12
                
                # Calculate time saved
                base_months = int(loan_amount / principal_payment)
                time_saved = base_months - months_with_extra
                years_saved = time_saved // 12
                months_saved = time_saved % 12
            else:
                years_to_payoff = int(loan_amount / (principal_payment * 12))
                months_to_payoff = 0
                years_saved = months_saved = 0
                interest_saved = 0

            # Get currency symbol
            currency = self.currency_var.get()

            # Update display values
            self.monthly_payment_var.set(f"{self.currency_var.get()}{total_monthly:,.0f}")
            self.total_interest_var.set(f"{self.currency_var.get()}{total_interest:,.0f}")
            self.monthly_principal_var.set(f"{currency}{principal_payment:,.0f}")
            self.monthly_extra_var.set(f"{currency}{extra_payment:,.0f}")
            self.monthly_total_principal_var.set(f"{currency}{(principal_payment + extra_payment):,.0f}")
            self.monthly_interest_var.set(f"{currency}{monthly_interest:,.0f}")
            self.monthly_fee_var.set(f"{monthly_fee:,.0f}")
            self.monthly_total_var.set(f"{currency}{total_monthly:,.0f}")
            self.time_saved_var.set(f"{years_saved} years, {months_saved} months")
            self.interest_saved_var.set(f"{currency}{interest_saved:,.0f}")
            self.loan_payoff_time_var.set(f"{years_to_payoff} years, {months_to_payoff} months")

            # Store values for PDF export with proper formatting
            self.current_values = {
                'loan_amount': loan_amount,
                'loan_seeking': loan_seeking,
                'down_payment': down_payment,
                'currency_symbol': currency,
                'monthly_payment': total_monthly,
                'total_interest': total_interest,
                'principal_payment': principal_payment,
                'extra_payment': extra_payment,
                'monthly_fee': monthly_fee,
                'time_saved': f"{years_saved} years, {months_saved} months",
                'interest_saved': interest_saved,
                'loan_payoff': f"{years_to_payoff} years, {months_to_payoff} months"
            }

            # Update visualization
            self.update_yearly_visualization(
                loan_amount,
                monthly_rate,
                years_to_payoff,
                principal_payment,
                extra_payment,
                monthly_fee
            )

            return True

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during calculation: {str(e)}")
            return False

    def update_yearly_visualization(self, loan_amount, monthly_rate, years, principal_payment, extra_payment, monthly_fee):
        """Update the visualization with yearly payment breakdown"""
        self.ax.clear()

        # Calculate yearly totals
        years_range = range(1, years + 1) if years > 0 else range(1, 2)
        base_principal = principal_payment * 12
        extra_principal = extra_payment * 12
        yearly_base_principal = [base_principal] * len(years_range)
        yearly_extra_principal = [extra_principal] * len(years_range)
        yearly_interest = []
        yearly_total = []
        
        remaining_balance = loan_amount
        for _ in years_range:
            yearly_interest_total = 0
            for _ in range(12):
                if remaining_balance <= 0:
                    break
                monthly_interest = remaining_balance * monthly_rate
                yearly_interest_total += monthly_interest
                remaining_balance -= (principal_payment + extra_payment)
            yearly_interest.append(yearly_interest_total)
            yearly_total.append(base_principal + extra_principal + yearly_interest_total + (monthly_fee * 12))

        # Create the bar plot
        x = np.arange(len(years_range))
        width = 0.2

        # Plot base principal and stack extra payment on top
        base_bars = self.ax.bar(x - width*0.5, yearly_base_principal, width, label='Base Principal', color='#2ecc71')
        extra_bars = self.ax.bar(x - width*0.5, yearly_extra_principal, width, label='Extra Principal', color='#FFA500', bottom=yearly_base_principal)
        
        # Plot interest and total bars separately
        self.ax.bar(x + width*0.5, yearly_interest, width, label='Interest', color='#e74c3c')
        self.ax.bar(x + width*1.5, yearly_total, width, label='Total', color='#3498db')

        # Customize plot
        currency = self.currency_var.get()
        self.ax.set_ylabel(f'Amount ({currency})')
        self.ax.set_xlabel('Year')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels([str(i) for i in years_range])
        self.ax.legend()

        # Add grid
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Rotate labels
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')

        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()

    def get_float_value(self, value_str):
        """Convert string to float, handling commas/periods and invalid input"""
        try:
            # Remove any currency symbols
            cleaned_str = value_str.replace('kr', '').replace('$', '').strip()
            # Replace comma with period for decimal numbers
            cleaned_str = cleaned_str.replace(',', '.')
            # Remove any additional periods (if more than one exists)
            if cleaned_str.count('.') > 1:
                first_period = cleaned_str.find('.')
                cleaned_str = cleaned_str[:first_period + 1] + cleaned_str[first_period + 1:].replace('.', '')
            if not cleaned_str:
                return 0.0
            return float(cleaned_str)
        except ValueError:
            raise ValueError(f"Invalid number format: {value_str}")

    def update_on_loan_seeking_change(self, *args):
        """Update loan amount when loan seeking amount changes"""
        try:
            loan_seeking_str = self.loan_seeking_var.get().strip()
            if not loan_seeking_str:
                self.down_payment_var.set("")
                self.loan_amount_var.set("")
                return

            loan_seeking = self.get_float_value(loan_seeking_str)
            
            if loan_seeking > 0:
                if self.down_payment_mode.get() == "auto":
                    # Calculate 15% down payment for auto mode
                    down_payment = loan_seeking * 0.15
                    self.down_payment_var.set(f"{down_payment:,.0f}")
                    self.down_payment_entry.configure(state='disabled')
                    
                    # Calculate and store loan amount
                    loan_amount = loan_seeking - down_payment
                    self.loan_amount_var.set(f"{loan_amount:,.0f}")
                    
                    # Update current values
                    self.current_values['loan_seeking'] = float(loan_seeking)
                    self.current_values['down_payment'] = float(down_payment)
                    self.current_values['loan_amount'] = float(loan_amount)
                else:
                    # In manual mode, enable entry
                    self.down_payment_entry.configure(state='normal')
                    # If down payment is empty or invalid, set it to 0
                    try:
                        down_payment = self.get_float_value(self.down_payment_var.get())
                        if down_payment <= 0:
                            self.down_payment_var.set("0")
                            down_payment = 0
                    except ValueError:
                        self.down_payment_var.set("0")
                        down_payment = 0
                    # Calculate loan amount
                    loan_amount = loan_seeking - down_payment
                    self.loan_amount_var.set(f"{loan_amount:,.0f}")
            else:
                # Clear fields if loan seeking is not positive
                self.down_payment_entry.configure(state='disabled')
                self.down_payment_var.set("")
                self.loan_amount_var.set("")

        except ValueError:
            # Handle any conversion errors
            self.down_payment_entry.configure(state='disabled')
            self.down_payment_var.set("")
            self.loan_amount_var.set("")

    def update_loan_amount(self, *args):
        """Update loan amount when down payment changes"""
        try:
            loan_seeking = self.get_float_value(self.loan_seeking_var.get())
            down_payment = self.get_float_value(self.down_payment_var.get())
            if loan_seeking > 0 and down_payment > 0:
                loan_amount = loan_seeking - down_payment if down_payment <= loan_seeking else 0
                self.loan_amount_var.set(f"{loan_amount:,.0f}")
        except ValueError:
            pass

    def toggle_down_payment_mode(self):
        """Toggle down payment mode between auto and manual"""
        loan_seeking_str = self.loan_seeking_var.get().strip()
        
        if self.down_payment_mode.get() == "auto":
            # Switch to auto mode
            try:
                if loan_seeking_str:
                    loan_seeking = self.get_float_value(loan_seeking_str)
                    if loan_seeking > 0:
                        # Calculate and set 15% down payment
                        down_payment = loan_seeking * 0.15
                        self.down_payment_var.set(f"{down_payment:,.0f}")
                        
                        # Update loan amount and variables
                        loan_amount = loan_seeking - down_payment
                        self.loan_amount_var.set(f"{loan_amount:,.0f}")
                        
                        # Update current values
                        self.current_values['loan_seeking'] = float(loan_seeking)
                        self.current_values['down_payment'] = float(down_payment)
                        self.current_values['loan_amount'] = float(loan_amount)
            except ValueError:
                pass
            self.down_payment_entry.configure(state='disabled')
        else:
            # Switch to manual mode
            self.down_payment_entry.configure(state='normal')
            try:
                # Get current values
                loan_seeking = self.get_float_value(self.loan_seeking_var.get() or "0")
                down_payment = self.get_float_value(self.down_payment_var.get() or "0")
                
                # Validate and set down payment
                if down_payment <= 0:
                    self.down_payment_var.set("0")
                    down_payment = 0
                
                # Calculate and store loan amount
                loan_amount = loan_seeking - down_payment if down_payment < loan_seeking else 0
                self.loan_amount_var.set(f"{loan_amount:,.0f}")
                
                # Update current values
                self.current_values['loan_seeking'] = float(loan_seeking)
                self.current_values['down_payment'] = float(down_payment)
                self.current_values['loan_amount'] = float(loan_amount)
            except ValueError:
                self.down_payment_var.set("0")
                self.current_values['down_payment'] = 0.0

    def initialize_variables(self):
        """Initialize all variables"""
        # Currency
        self.currency_var = tk.StringVar(value="kr")
        self.currency_name_var = tk.StringVar(value="Swedish Krona (SEK)")

        # Input variables
        self.loan_seeking_var = tk.StringVar(value="")
        self.down_payment_var = tk.StringVar(value="")
        self.loan_amount_var = tk.StringVar(value="")
        self.interest_rate_var = tk.StringVar(value="4.5")  # Set default to 4.5
        self.principal_payment_var = tk.StringVar(value="")
        self.extra_payment_var = tk.StringVar(value="")
        self.monthly_fee_var = tk.StringVar(value="")

        # Result variables
        self.monthly_payment_var = tk.StringVar(value="kr0")
        self.total_interest_var = tk.StringVar(value="kr0")
        self.monthly_principal_var = tk.StringVar(value="kr0")
        self.monthly_extra_var = tk.StringVar(value="kr0")
        self.monthly_total_principal_var = tk.StringVar(value="kr0")
        self.monthly_interest_var = tk.StringVar(value="kr0")
        self.monthly_fee_var = tk.StringVar(value="")  # Keep Monthly House Fee blank
        self.monthly_total_var = tk.StringVar(value="kr0")
        self.time_saved_var = tk.StringVar(value="0 years, 0 months")
        self.interest_saved_var = tk.StringVar(value="kr0")
        self.loan_payoff_time_var = tk.StringVar(value="0 years, 0 months")

        # Store current values for PDF export with proper initialization
        self.current_values = {
            'loan_amount': 0.0,
            'loan_seeking': 0.0,
            'down_payment': 0.0,
            'currency_symbol': 'kr',
            'monthly_payment': 0.0,
            'total_interest': 0.0,
            'principal_payment': 0.0,
            'extra_payment': 0.0,
            'monthly_fee': 0.0,
            'time_saved': '0 years, 0 months',
            'interest_saved': 0.0,
            'loan_payoff': '30 years, 0 months'
        }

    def initialize_display_variables(self):
        """Initialize display variables for results"""
        self.monthly_payment_var = tk.StringVar(value="kr0")
        self.total_interest_var = tk.StringVar(value="kr0")
        self.monthly_principal_var = tk.StringVar(value="kr0")
        self.monthly_extra_var = tk.StringVar(value="kr0")
        self.monthly_total_principal_var = tk.StringVar(value="kr0")
        self.monthly_interest_var = tk.StringVar(value="kr0")
        self.monthly_fee_var = tk.StringVar(value="")  # Keep Monthly House Fee blank
        self.monthly_total_var = tk.StringVar(value="kr0")
        self.time_saved_var = tk.StringVar(value="0 years, 0 months")
        self.interest_saved_var = tk.StringVar(value="kr0")
        self.loan_payoff_time_var = tk.StringVar(value="30 years, 0 months")

    def export_pdf(self):
        """Export results to PDF in landscape mode with plot"""
        try:
            # Create exports directory if it doesn't exist
            export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
            os.makedirs(export_dir, exist_ok=True)

            # Generate timestamp for unique filename
            current_date = datetime.now()
            base_filename = f'mortgage_calculation_{current_date.strftime("%d-%m-%Y")}'

            # Check if file exists and create unique name
            counter = 1
            filename = os.path.join(export_dir, f'{base_filename}.pdf')
            while os.path.exists(filename):
                filename = os.path.join(export_dir, f'{base_filename}_{counter}.pdf')
                counter += 1

            # Create PDF in landscape mode
            width, height = landscape(A4)
            c = canvas.Canvas(filename, pagesize=landscape(A4))

            # Create figure for PDF with specified size of 15x3.5 inches
            pdf_fig = plt.Figure(figsize=(15, 3.5))
            pdf_ax = pdf_fig.add_subplot(111)
            pdf_fig.patch.set_facecolor('white')  # Ensure white background
            
            # Copy plot data and styling
            x = self.ax.get_xticks()
            width_bar = 0.2
            
            # Get data from current plot
            for rect in self.ax.containers:
                data = [p.get_height() for p in rect]
                label = rect.get_label()
                color = rect.get_children()[0].get_facecolor()
                
                if label == 'Base Principal':
                    pdf_ax.bar(x - width_bar*0.5, data, width_bar, label=label, color=color)
                elif label == 'Extra Principal':
                    bottom = [p.get_height() for p in self.ax.containers[0]]
                    pdf_ax.bar(x - width_bar*0.5, data, width_bar, label=label, color=color, bottom=bottom)
                elif label == 'Interest':
                    pdf_ax.bar(x + width_bar*0.5, data, width_bar, label=label, color=color)
                elif label == 'Total':
                    pdf_ax.bar(x + width_bar*1.5, data, width_bar, label=label, color=color)
            
            # Copy styling
            pdf_ax.set_ylabel(self.ax.get_ylabel())
            pdf_ax.set_xlabel(self.ax.get_xlabel())
            pdf_ax.set_xticks(x)
            pdf_ax.set_xticklabels([str(i+1) for i in range(len(x))])
            pdf_ax.legend()
            pdf_ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            plt.setp(pdf_ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add title for print version
            pdf_ax.set_title('Mortgage Payment Breakdown by Year', pad=20)
            
            # Adjust layout
            pdf_fig.tight_layout()
            
            # Convert plot to PNG for PDF inclusion
            plot_filename = 'temp_plot.png'
            pdf_fig.savefig(plot_filename, dpi=300, bbox_inches='tight')

            # Title
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 40, "Mortgage Calculator Results")
            
            # Add line under title
            c.line(50, height - 50, width - 50, height - 50)
            
            # Generation timestamp
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Generated on: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get values from stored calculations
            currency = self.currency_var.get()
            loan_seeking = self.current_values['loan_seeking']
            down_payment = self.current_values['down_payment']
            loan_amount = self.current_values['loan_amount']

            # Ensure we have valid values
            if loan_seeking <= 0 or loan_amount <= 0:
                messagebox.showerror("Error", "Please calculate loan details before exporting to PDF")
                return

            # Two-column layout for details
            left_col_x = 50
            right_col_x = width/2 + 50
            y = height - 100

            # Left Column
            # Loan Details
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_col_x, y, "Loan Details")
            c.setFont("Helvetica", 10)
            y -= 20

            currency = self.currency_var.get()
            details = [
                f"Loan Seeking For: {currency}{loan_seeking:,.2f}",
                f"Down Payment: {currency}{down_payment:,.2f}",
                f"Loan Amount: {currency}{loan_amount:,.2f}",
                f"Interest Rate: {self.interest_rate_var.get()}%"
            ]
            
            for detail in details:
                c.drawString(left_col_x + 20, y, detail)
                y -= 15

            # Monthly Payment Breakdown (continuing in left column)
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_col_x, y, "Monthly Payment Breakdown")
            c.setFont("Helvetica", 10)
            y -= 20
            
            breakdown = [
                f"Principal Payment: {self.monthly_principal_var.get()}",
                f"Extra Payment: {self.monthly_extra_var.get()}",
                f"Total Principal: {self.monthly_total_principal_var.get()}",
                f"Interest Payment: {self.monthly_interest_var.get()}",
                f"Monthly House Fee: {self.monthly_fee_var.get() or 'kr0'}",
                f"Total Monthly Payment: {self.monthly_total_var.get()}"
            ]
            
            for item in breakdown:
                c.drawString(left_col_x + 20, y, item)
                y -= 15

            # Right Column
            y = height - 100

            # With Extra Payments
            c.setFont("Helvetica-Bold", 12)
            c.drawString(right_col_x, y, "With Extra Payments")
            c.setFont("Helvetica", 10)
            y -= 20
            
            extra_payments = [
                f"Time Saved: {self.time_saved_var.get()}",
                f"Interest Saved: {self.interest_saved_var.get()}"
            ]
            
            for item in extra_payments:
                c.drawString(right_col_x + 20, y, item)
                y -= 15

            # Loan Payoff Time
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(right_col_x, y, "Loan Payoff Time")
            c.setFont("Helvetica", 10)
            y -= 20
            c.drawString(right_col_x + 20, y, f"{self.loan_payoff_time_var.get()}")

            # Position the plot at the bottom with specified dimensions
            plot_margin = 50
            plot_height = 175  # approximately 3.5 inches at 72 DPI
            plot_width = 750   # approximately 15 inches at 72 DPI
            plot_y = plot_margin + 40  # Leave space for the note at bottom
            
            # Draw the plot with preserved aspect ratio
            c.drawImage(plot_filename, plot_margin, plot_y,
                       width=plot_width, height=plot_height,
                       preserveAspectRatio=True)

            # Add dividing line above plot
            c.line(50, plot_y + plot_height + 10, width - 50, plot_y + plot_height + 10)

            # Add "Plot:" label above the plot
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, plot_y + plot_height + 20, "Plot:")

            # Add note about calculations at the bottom
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, "*Note: Calculations are based on the entered loan amount, interest rate, and payment schedule.")
            
            c.save()
            
            try:
                # Clean up temporary plot file
                os.remove(plot_filename)
            except Exception:
                pass  # Ignore cleanup errors
            
            messagebox.showinfo("Success", f"PDF exported successfully to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
            try:
                # Clean up temporary file if it exists
                if os.path.exists('temp_plot.png'):
                    os.remove('temp_plot.png')
            except Exception:
                pass  # Ignore cleanup errors

    def update_extra_payments_info(self, time_saved, interest_saved):
        """Update the extra payments information display"""
        self.time_saved_var.set(str(time_saved))
        self.interest_saved_var.set(str(interest_saved))

    def clear_displays(self):
        """Clear all display fields"""
        currency = self.currency_var.get()
        self.monthly_payment_var.set(f"{currency}0")
        self.total_interest_var.set(f"{currency}0")
        self.monthly_principal_var.set(f"{currency}0")
        self.monthly_extra_var.set(f"{currency}0")
        self.monthly_total_principal_var.set(f"{currency}0")
        self.monthly_interest_var.set(f"{currency}0")
        self.monthly_fee_var.set("")  # Keep Monthly House Fee blank
        self.monthly_total_var.set(f"{currency}0")
        self.time_saved_var.set("0 years, 0 months")
        self.interest_saved_var.set(f"{currency}0")
        self.loan_payoff_time_var.set("30 years, 0 months")

    def clear_fields(self):
        """Clear all input fields and reset displays"""
        # Clear input fields
        self.loan_seeking_var.set("")
        self.down_payment_var.set("")
        self.interest_rate_var.set("4.5")  # Reset interest rate to default
        self.principal_payment_var.set("")
        self.extra_payment_var.set("")
        self.monthly_fee_var.set("")

        # Reset currency to default
        self.currency_var.set('kr')
        self.currency_name_var.set("Swedish Krona (SEK)")

        # Reset loan amount
        self.loan_amount_var.set("0")

        # Clear displays
        self.clear_displays()

        # Clear visualization with empty plot
        self.ax.clear()
        self.ax.set_xlabel('Year')
        self.ax.set_ylabel('Amount')
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        self.figure.tight_layout()
        self.canvas.draw()

# STEP 13: Main Function
def main():
    root = tk.Tk()
    app = MortgageCalculator(root)
    root.mainloop()

# STEP 14: Entry Point
if __name__ == "__main__":
    main()
