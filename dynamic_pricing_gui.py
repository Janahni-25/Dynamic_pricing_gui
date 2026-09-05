import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
import os
import csv
import json
import random

class DynamicPricingEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Dynamic Pricing Engine")
        self.root.geometry("1400x800")
        self.root.configure(bg="#6ed8ed")
        self.TRANSPORT_FACTOR = 1.05
        self.WAREHOUSE_COST_FACTOR = 0.98
        self.SUPPLIER_AVAILABILITY_FACTOR = 1.02
        self.pricing_history = []
        self.csv_filename = "pricing_history.csv"
        self.load_historical_data()
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        title_label = ttk.Label(main_frame, text="Dynamic Pricing Engine", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(1, weight=1)
        self.create_pricing_tab(notebook)
        self.create_history_tab(notebook)
        self.create_analytics_tab(notebook)

    def create_pricing_tab(self, notebook):
        pricing_frame = ttk.Frame(notebook, padding="10")
        notebook.add(pricing_frame, text="Price Calculator")
        pricing_frame.columnconfigure(1, weight=1)
        core_frame = ttk.LabelFrame(pricing_frame, text="Core Input Factors", padding="10")
        core_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        core_frame.columnconfigure(1, weight=1)
        self.input_vars = {}
        
        inputs = [
            ('Base Cost ($):', 'base_cost', tk.DoubleVar, 100.0),
            ('Desired Margin (%):', 'margin', tk.DoubleVar, 25.0),
            ('Competitor Price ($):', 'competitor_price', tk.DoubleVar, 130.0),
            ('Current Inventory:', 'inventory_level', tk.IntVar, 100),
            ('Max Inventory:', 'max_inventory', tk.IntVar, 500),
            ('Sales Velocity (units/day):', 'sales_velocity', tk.DoubleVar, 10.0),
            ('Avg Sales Velocity:', 'avg_sales_velocity', tk.DoubleVar, 8.0),
            ('Customer Type:', 'customer_type', tk.StringVar, 'regular'),
            ('Promotion (%):', 'promotion', tk.DoubleVar, 0.0),
        ]

        for i, (label, key, var_type, default) in enumerate(inputs[:7]):
            ttk.Label(core_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.input_vars[key] = var_type(value=default)
            ttk.Entry(core_frame, textvariable=self.input_vars[key], width=15).grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(core_frame, text=inputs[7][0]).grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.input_vars['customer_type'] = tk.StringVar(value='regular')
        ttk.Combobox(core_frame, textvariable=self.input_vars['customer_type'],
                     values=["vip", "loyal", "regular", "new", "student"], width=12).grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(core_frame, text=inputs[8][0]).grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.input_vars['promotion'] = tk.DoubleVar(value=0.0)
        ttk.Entry(core_frame, textvariable=self.input_vars['promotion'], width=15).grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        time_frame = ttk.LabelFrame(pricing_frame, text="Time & Market Factors", padding="10")
        time_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        time_frame.columnconfigure(1, weight=1)

        time_inputs = [
            ('Hour of Day (0-23):', 'hour', tk.IntVar, datetime.now().hour),
            ('Day of Week:', 'day_of_week', tk.StringVar, datetime.now().strftime("%A").lower()),
            ('Season:', 'season', tk.StringVar, 'spring'),
            ('Holiday/Festival:', 'is_holiday', tk.BooleanVar, False),
            ('Demand Index (0-1):', 'demand_index', tk.DoubleVar, 0.5),
            ('Price Elasticity:', 'elasticity', tk.DoubleVar, 1.0),
        ]

        ttk.Label(time_frame, text=time_inputs[0][0]).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_vars['hour'] = tk.IntVar(value=time_inputs[0][3])
        ttk.Entry(time_frame, textvariable=self.input_vars['hour'], width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(time_frame, text=time_inputs[1][0]).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.input_vars['day_of_week'] = tk.StringVar(value=time_inputs[1][3])
        ttk.Combobox(time_frame, textvariable=self.input_vars['day_of_week'],
                     values=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], width=12).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(time_frame, text=time_inputs[2][0]).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.input_vars['season'] = tk.StringVar(value=time_inputs[2][3])
        ttk.Combobox(time_frame, textvariable=self.input_vars['season'],
                     values=["spring", "summer", "autumn", "winter"], width=12).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(time_frame, text=time_inputs[3][0]).grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.input_vars['is_holiday'] = tk.BooleanVar(value=time_inputs[3][3])
        ttk.Checkbutton(time_frame, variable=self.input_vars['is_holiday']).grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(time_frame, text=time_inputs[4][0]).grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.input_vars['demand_index'] = tk.DoubleVar(value=time_inputs[4][3])
        ttk.Entry(time_frame, textvariable=self.input_vars['demand_index'], width=15).grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(time_frame, text=time_inputs[5][0]).grid(row=2, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.input_vars['elasticity'] = tk.DoubleVar(value=time_inputs[5][3])
        ttk.Entry(time_frame, textvariable=self.input_vars['elasticity'], width=15).grid(row=2, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Button(pricing_frame, text="Calculate Dynamic Price", command=self.calculate_price).grid(row=2, column=0, columnspan=2, pady=20)

        results_frame = ttk.LabelFrame(pricing_frame, text="Pricing Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)

        self.result_vars = {}

        labels = ['Final Price:', 'Price Change:', 'Markup:']
        keys = ['final_price', 'price_change', 'markup']
        defaults = ["$0.00", "0.00%", "0.00%"]
        colors = ['green', 'black', 'black']
        fonts = [('Arial', 12, 'bold'), ('Arial', 10), ('Arial', 10)]
        for i, (label_text, key, default, color, font) in enumerate(zip(labels, keys, defaults, colors, fonts)):
            ttk.Label(results_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.result_vars[key] = tk.StringVar(value=default)
            ttk.Label(results_frame, textvariable=self.result_vars[key], font=font,
                      foreground=color).grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        button_frame = ttk.Frame(pricing_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        buttons = [
            ("Save to History", self.save_to_history),
            ("Load Configuration", self.load_config),
            ("Save Configuration", self.save_config),
            ("Generate Sample Data", self.generate_sample_data),
            ("What-If Simulation", self.run_simulation),
        ]

        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=cmd).grid(row=0, column=i, padx=5)

    def create_history_tab(self, notebook):
        history_frame = ttk.Frame(notebook, padding="10")
        notebook.add(history_frame, text="Price History")

        controls_frame = ttk.Frame(history_frame)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        buttons = [
            ("Refresh History", self.refresh_history),
            ("Export CSV", self.export_history),
            ("Export Report", self.export_report),
            ("Clear History", self.clear_history),
        ]

        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(controls_frame, text=text, command=cmd).grid(row=0, column=i, padx=5)

        self.history_tree = ttk.Treeview(history_frame,
                                         columns=('timestamp', 'base_cost', 'final_price', 'markup', 'factors'),
                                         show='headings')
        self.history_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        headings = ['timestamp', 'base_cost', 'final_price', 'markup', 'factors']
        texts = ['Timestamp', 'Base Cost', 'Final Price', 'Markup %', 'Key Factors']
        widths = [150, 100, 100, 100, 300]

        for h, t, w in zip(headings, texts, widths):
            self.history_tree.heading(h, text=t)
            self.history_tree.column(h, width=w)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

    def create_analytics_tab(self, notebook):
        analytics_frame = ttk.Frame(notebook, padding="10")
        notebook.add(analytics_frame, text="Analytics")

        chart_controls = ttk.Frame(analytics_frame)
        chart_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        buttons = [
            ("Price Trend", self.show_price_trend),
            ("Factor Impact", self.show_factor_impact),
            ("Demand Analysis", self.show_demand_analysis),
        ]

        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(chart_controls, text=text, command=cmd).grid(row=0, column=i, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, analytics_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        analytics_frame.columnconfigure(0, weight=1)
        analytics_frame.rowconfigure(1, weight=1)

    def calculate_inventory_factor(self):
        ratio = self.input_vars['inventory_level'].get() / max(self.input_vars['max_inventory'].get(), 1)
        # Sigmoid function for smooth mapping between 0.9 and 1.15
        factor = 0.9 + (1.15 - 0.9) / (1 + np.exp(-12 * (0.5 - ratio)))
        return float(factor)

    def calculate_demand_factor(self):
        sv = self.input_vars['sales_velocity'].get()
        avg_sv = self.input_vars['avg_sales_velocity'].get()
        demand_idx = self.input_vars['demand_index'].get()
        elasticity = self.input_vars['elasticity'].get()

        velocity_ratio = sv / avg_sv if avg_sv > 0 else 1.0
        velocity_factor = 1 + 0.1 * (velocity_ratio - 1)

        demand_factor = 0.9 + 0.2 * demand_idx
        elasticity_factor = 1 / elasticity if elasticity > 0 else 1.0

        return velocity_factor * demand_factor * elasticity_factor

    def calculate_competitor_factor(self, price):
        competitor_price = self.input_vars['competitor_price'].get()
        if competitor_price <= 0:
            return 1.0
        ratio = price / competitor_price
        # Smooth adjustment around parity price
        return 1.0 - 0.1 * np.tanh(10 * (ratio - 1))

    def calculate_time_factor(self):
        hour = self.input_vars['hour'].get()
        day = self.input_vars['day_of_week'].get()
        season = self.input_vars['season'].get()
        holiday = self.input_vars['is_holiday'].get()

        def gauss(x, mu, sigma, amp):
            return amp * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

        hour_factor = 1 + gauss(hour, 8, 2, -0.05) + gauss(hour, 12.5, 1.5, 0.1) + gauss(hour, 18.5, 2, 0.15)

        day_factor = 1.1 if day in ['friday', 'saturday', 'sunday'] else 1.0

        seasonal = {'spring': 1.0, 'summer': 1.05, 'autumn': 0.98, 'winter': 1.02}
        season_factor = seasonal.get(season, 1.0)

        holiday_factor = 1.2 if holiday else 1.0

        return hour_factor * day_factor * season_factor * holiday_factor

    def calculate_customer_factor(self):
        multipliers = {'vip': 0.90, 'loyal': 0.95, 'regular': 1.0, 'new': 0.98, 'student': 0.85}
        return multipliers.get(self.input_vars['customer_type'].get(), 1.0)

    def calculate_promotion_factor(self):
        return 1.0 - self.input_vars['promotion'].get() / 100

    def calculate_price(self):
        try:
            base_cost = self.input_vars['base_cost'].get()
            margin = self.input_vars['margin'].get() / 100
            base_price = base_cost * (1 + margin)

            factors = {
                'inventory_factor': self.calculate_inventory_factor(),
                'demand_factor': self.calculate_demand_factor(),
                'time_factor': self.calculate_time_factor(),
                'customer_factor': self.calculate_customer_factor(),
                'promotion_factor': self.calculate_promotion_factor(),
                'transport_factor': self.TRANSPORT_FACTOR,
                'warehouse_factor': self.WAREHOUSE_COST_FACTOR,
                'supplier_factor': self.SUPPLIER_AVAILABILITY_FACTOR,
            }

            price = base_price * np.prod([factors[k] for k in [
                'inventory_factor', 'demand_factor', 'time_factor', 'customer_factor', 'promotion_factor']])

            factors['competitor_factor'] = self.calculate_competitor_factor(price)
            price *= factors['competitor_factor']

            price *= factors['transport_factor'] * factors['warehouse_factor'] * factors['supplier_factor']

            price_change = (price - base_price) / base_price * 100
            markup = (price - base_cost) / base_cost * 100

            self.result_vars['final_price'].set(f"${price:.2f}")
            self.result_vars['price_change'].set(f"{price_change:+.2f}%")
            self.result_vars['markup'].set(f"{markup:.2f}%")

            self.current_calculation = {
                'timestamp': datetime.now(),
                'base_cost': base_cost,
                'base_price': base_price,
                'final_price': price,
                'markup_percentage': markup,
                'factors': factors,
                'inputs': {k: v.get() for k, v in self.input_vars.items()}
            }
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating price: {str(e)}")

    def save_to_history(self):
        if not hasattr(self, 'current_calculation'):
            messagebox.showwarning("No Calculation", "Please calculate a price first.")
            return

        self.pricing_history.append(self.current_calculation.copy())
        self.save_historical_data()
        self.refresh_history()
        messagebox.showinfo("Saved", "Calculation saved to history successfully!")

    def save_historical_data(self):
        try:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                header = ['timestamp', 'base_cost', 'base_price', 'final_price', 'markup_percentage',
                          'inventory_factor', 'demand_factor', 'competitor_factor', 'time_factor',
                          'customer_factor', 'promotion_factor', 'customer_type', 'season', 'is_holiday',
                          'hour', 'day_of_week', 'inventory_level', 'sales_velocity', 'demand_index']
                writer.writerow(header)
                for record in self.pricing_history:
                    row = [
                        record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        record['base_cost'],
                        record['base_price'],
                        record['final_price'],
                        record['markup_percentage'],
                        record['factors']['inventory_factor'],
                        record['factors']['demand_factor'],
                        record['factors'].get('competitor_factor', 1.0),
                        record['factors']['time_factor'],
                        record['factors']['customer_factor'],
                        record['factors']['promotion_factor'],
                        record['inputs']['customer_type'],
                        record['inputs']['season'],
                        record['inputs']['is_holiday'],
                        record['inputs']['hour'],
                        record['inputs']['day_of_week'],
                        record['inputs']['inventory_level'],
                        record['inputs']['sales_velocity'],
                        record['inputs']['demand_index']
                    ]
                    writer.writerow(row)
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving data: {str(e)}")

    def load_historical_data(self):
        try:
            if os.path.exists(self.csv_filename):
                self.pricing_history = []
                with open(self.csv_filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        record = {
                            'timestamp': datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                            'base_cost': float(row['base_cost']),
                            'base_price': float(row['base_price']),
                            'final_price': float(row['final_price']),
                            'markup_percentage': float(row['markup_percentage']),
                            'factors': {
                                'inventory_factor': float(row['inventory_factor']),
                                'demand_factor': float(row['demand_factor']),
                                'competitor_factor': float(row['competitor_factor']),
                                'time_factor': float(row['time_factor']),
                                'customer_factor': float(row['customer_factor']),
                                'promotion_factor': float(row['promotion_factor'])
                            },
                            'inputs': {
                                'customer_type': row['customer_type'],
                                'season': row['season'],
                                'is_holiday': row['is_holiday'].lower() == 'true',
                                'hour': int(row['hour']),
                                'day_of_week': row['day_of_week'],
                                'inventory_level': int(row['inventory_level']),
                                'sales_velocity': float(row['sales_velocity']),
                                'demand_index': float(row['demand_index'])
                            }
                        }
                        self.pricing_history.append(record)
        except Exception as e:
            print(f"Error loading historical data: {str(e)}")

    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for record in reversed(self.pricing_history[-50:]):
            timestamp = record['timestamp'].strftime('%Y-%m-%d %H:%M')
            base_cost = f"${record['base_cost']:.2f}"
            final_price = f"${record['final_price']:.2f}"
            markup = f"{record['markup_percentage']:.1f}%"
            factors = f"Inv:{record['factors']['inventory_factor']:.2f} Dem:{record['factors']['demand_factor']:.2f} Time:{record['factors']['time_factor']:.2f}"
            self.history_tree.insert('', 0, values=(timestamp, base_cost, final_price, markup, factors))

    def export_history(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                    title="Export Pricing History")
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    header = ['Timestamp', 'Product', 'Base Cost', 'Final Price', 'Markup %',
                              'Inventory Factor', 'Demand Factor', 'Competitor Factor', 'Time Factor',
                              'Customer Factor', 'Promotion Factor', 'Customer Type', 'Season',
                              'Holiday', 'Hour', 'Day of Week', 'Inventory Level', 'Sales Velocity',
                              'Demand Index', 'Price Change %']
                    writer.writerow(header)
                    for record in self.pricing_history:
                        price_change = ((record['final_price'] - record['base_price']) / record['base_price']) * 100
                        row = [
                            record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                            'Product',
                            f"${record['base_cost']:.2f}",
                            f"${record['final_price']:.2f}",
                            f"{record['markup_percentage']:.2f}%",
                            f"{record['factors']['inventory_factor']:.3f}",
                            f"{record['factors']['demand_factor']:.3f}",
                            f"{record['factors'].get('competitor_factor', 1.0):.3f}",
                            f"{record['factors']['time_factor']:.3f}",
                            f"{record['factors']['customer_factor']:.3f}",
                            f"{record['factors']['promotion_factor']:.3f}",
                            record['inputs']['customer_type'],
                            record['inputs']['season'],
                            'Yes' if record['inputs']['is_holiday'] else 'No',
                            record['inputs']['hour'],
                            record['inputs']['day_of_week'].title(),
                            record['inputs']['inventory_level'],
                            record['inputs']['sales_velocity'],
                            record['inputs']['demand_index'],
                            f"{price_change:+.2f}%"
                        ]
                        writer.writerow(row)
                messagebox.showinfo("Export Complete", f"History exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all pricing history?"):
            self.pricing_history = []
            self.refresh_history()
            if os.path.exists(self.csv_filename):
                os.remove(self.csv_filename)
            messagebox.showinfo("Cleared", "Pricing history cleared successfully!")

    def save_config(self):
        try:
            config = {'inputs': {k: v.get() for k, v in self.input_vars.items()},
                      'timestamp': datetime.now().isoformat()}
            filename = filedialog.asksaveasfilename(defaultextension=".json",
                                                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                    title="Save Configuration")
            if filename:
                with open(filename, 'w') as file:
                    json.dump(config, file, indent=2)
                messagebox.showinfo("Saved", f"Configuration saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving configuration: {str(e)}")

    def load_config(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                  title="Load Configuration")
            if filename:
                with open(filename, 'r') as file:
                    config = json.load(file)
                for key, value in config['inputs'].items():
                    if key in self.input_vars:
                        self.input_vars[key].set(value)
                messagebox.showinfo("Loaded", f"Configuration loaded from {filename}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading configuration: {str(e)}")

    def show_price_trend(self):
        if not self.pricing_history:
            messagebox.showwarning("No Data", "No historical data available for analysis.")
            return
        self.ax.clear()
        timestamps = [record['timestamp'] for record in self.pricing_history]
        final_prices = [record['final_price'] for record in self.pricing_history]
        base_prices = [record['base_price'] for record in self.pricing_history]

        self.ax.plot(timestamps, final_prices, label='Final Price', marker='o', linewidth=2)
        self.ax.plot(timestamps, base_prices, label='Base Price', marker='s', linewidth=2, alpha=0.7)

        self.ax.set_title('Price Trend Over Time')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price ($)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)

        self.fig.tight_layout()
        self.canvas.draw()

    def show_factor_impact(self):
        if not self.pricing_history:
            messagebox.showwarning("No Data", "No historical data available for analysis.")
            return
        self.ax.clear()
        factors = ['inventory_factor', 'demand_factor', 'competitor_factor', 'time_factor', 'customer_factor', 'promotion_factor']

        avg_factors = {factor: np.mean([record['factors'].get(factor, 1.0) for record in self.pricing_history]) for factor in factors}

        factor_names = [name.replace('_factor', '').title() for name in factors]
        factor_values = [avg_factors[factor] for factor in factors]

        bars = self.ax.bar(factor_names, factor_values, alpha=0.7)
        for bar, value in zip(bars, factor_values):
            bar.set_color('green' if value > 1.0 else 'red' if value < 1.0 else 'blue')

        self.ax.set_title('Average Factor Impact on Pricing')
        self.ax.set_ylabel('Factor Multiplier')
        self.ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Neutral (1.0)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)

        self.fig.tight_layout()
        self.canvas.draw()

    def show_demand_analysis(self):
        if not self.pricing_history:
            messagebox.showwarning("No Data", "No historical data available for analysis.")
            return

        self.ax.clear()
        demand_indices = [record['inputs']['demand_index'] for record in self.pricing_history]
        final_prices = [record['final_price'] for record in self.pricing_history]

        scatter = self.ax.scatter(demand_indices, final_prices, alpha=0.6, c=range(len(demand_indices)), cmap='viridis')

        if len(demand_indices) > 1:
            z = np.polyfit(demand_indices, final_prices, 1)
            p = np.poly1d(z)
            self.ax.plot(demand_indices, p(demand_indices), "r--", alpha=0.8, linewidth=2)

        self.ax.set_title('Price vs Demand Index Analysis')
        self.ax.set_xlabel('Demand Index')
        self.ax.set_ylabel('Final Price ($)')
        self.ax.grid(True, alpha=0.3)

        cbar = plt.colorbar(scatter, ax=self.ax)
        cbar.set_label('Time Order')

        self.fig.tight_layout()
        self.canvas.draw()

    def run_simulation(self):
        simulation_window = tk.Toplevel(self.root)
        simulation_window.title("What-If Simulation")
        simulation_window.geometry("600x400")

        ttk.Label(simulation_window, text="Simulate Price Changes", font=('Arial', 12, 'bold')).pack(pady=10)

        sim_frame = ttk.Frame(simulation_window, padding="10")
        sim_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(sim_frame, text="Select Scenario:").grid(row=0, column=0, sticky=tk.W, pady=5)
        scenario_var = tk.StringVar(value="inventory_change")
        scenario_combo = ttk.Combobox(sim_frame, textvariable=scenario_var,
                                      values=["inventory_change", "demand_surge", "competitor_price_drop", "holiday_period"])
        scenario_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        results_text = tk.Text(sim_frame, height=15, width=70)
        results_text.grid(row=1, column=0, columnspan=2, pady=10)

        scrollbar = ttk.Scrollbar(sim_frame, orient=tk.VERTICAL, command=results_text.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        results_text.configure(yscrollcommand=scrollbar.set)

        def run_selected_simulation():
            scenario = scenario_var.get()
            results_text.delete(1.0, tk.END)

            base_inputs = {k: v.get() for k, v in self.input_vars.items()}

            results_text.insert(tk.END, f"=== {scenario.replace('_', ' ').title()} Simulation ===\n\n")
            results_text.insert(tk.END, f"Base Configuration:\n")
            results_text.insert(tk.END, f"Base Cost: ${base_inputs['base_cost']:.2f}\n")
            results_text.insert(tk.END, f"Current Inventory: {base_inputs['inventory_level']}\n\n")

            if scenario == "inventory_change":
                inventory_levels = [50, 100, 200, 400, 500]
                results_text.insert(tk.END, "Inventory Level Impact:\n")
                for inv_level in inventory_levels:
                    self.input_vars['inventory_level'].set(inv_level)
                    self.calculate_price()
                    if hasattr(self, 'current_calculation'):
                        price = self.current_calculation['final_price']
                        results_text.insert(tk.END, f"Inventory {inv_level}: ${price:.2f}\n")

            elif scenario == "demand_surge":
                demand_indices = [0.2, 0.4, 0.6, 0.8, 1.0]
                results_text.insert(tk.END, "Demand Index Impact:\n")
                for demand in demand_indices:
                    self.input_vars['demand_index'].set(demand)
                    self.calculate_price()
                    if hasattr(self, 'current_calculation'):
                        price = self.current_calculation['final_price']
                        results_text.insert(tk.END, f"Demand {demand}: ${price:.2f}\n")

            for key, value in base_inputs.items():
                self.input_vars[key].set(value)

        ttk.Button(sim_frame, text="Run Simulation", command=run_selected_simulation).grid(row=2, column=0, columnspan=2, pady=10)

    def generate_sample_data(self):
        if messagebox.askyesno("Generate Sample Data", "Generate 20 sample pricing records for testing?"):
            base_time = datetime.now() - timedelta(days=30)
            for i in range(20):
                self.input_vars['base_cost'].set(random.uniform(80, 150))
                self.input_vars['margin'].set(random.uniform(15, 35))
                self.input_vars['competitor_price'].set(random.uniform(100, 180))
                self.input_vars['inventory_level'].set(random.randint(50, 500))
                self.input_vars['sales_velocity'].set(random.uniform(5, 20))
                self.input_vars['demand_index'].set(random.uniform(0.2, 0.9))
                self.input_vars['hour'].set(random.randint(8, 22))
                self.input_vars['customer_type'].set(random.choice(['vip', 'loyal', 'regular', 'new']))
                self.input_vars['is_holiday'].set(random.choice([True, False]))

                self.calculate_price()
                if hasattr(self, 'current_calculation'):
                    self.current_calculation['timestamp'] = base_time + timedelta(days=i, hours=random.randint(0, 23))
                    self.pricing_history.append(self.current_calculation.copy())
            self.save_historical_data()
            self.refresh_history()
            messagebox.showinfo("Sample Data", "20 sample records generated successfully!")

    def export_report(self):
        if not self.pricing_history:
            messagebox.showwarning("No Data", "No historical data available for report.")
            return
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                    title="Export Pricing Report")
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    writer.writerow(["=== DYNAMIC PRICING REPORT ==="])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([f"Total Records: {len(self.pricing_history)}"])
                    writer.writerow([])

                    prices = [record['final_price'] for record in self.pricing_history]
                    base_costs = [record['base_cost'] for record in self.pricing_history]
                    markups = [record['markup_percentage'] for record in self.pricing_history]

                    writer.writerow(["=== PRICE STATISTICS ==="])
                    writer.writerow(["Metric", "Value"])
                    writer.writerow([f"Average Final Price", f"${np.mean(prices):.2f}"])
                    writer.writerow([f"Min Final Price", f"${np.min(prices):.2f}"])
                    writer.writerow([f"Max Final Price", f"${np.max(prices):.2f}"])
                    writer.writerow([f"Average Base Cost", f"${np.mean(base_costs):.2f}"])
                    writer.writerow([f"Average Markup", f"{np.mean(markups):.2f}%"])
                    writer.writerow([])

                    writer.writerow(["=== DETAILED PRICING DATA ==="])
                    writer.writerow(['Timestamp', 'Base Cost', 'Final Price', 'Markup %', 'Customer Type',
                                     'Season', 'Holiday', 'Inventory Level', 'Demand Index'])

                    for record in self.pricing_history:
                        writer.writerow([
                            record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                            f"${record['base_cost']:.2f}",
                            f"${record['final_price']:.2f}",
                            f"{record['markup_percentage']:.2f}%",
                            record['inputs']['customer_type'],
                            record['inputs']['season'],
                            'Yes' if record['inputs']['is_holiday'] else 'No',
                            record['inputs']['inventory_level'],
                            record['inputs']['demand_index']
                        ])

                messagebox.showinfo("Report Exported", f"Comprehensive report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report: {str(e)}")


def main():
    try:
        root = tk.Tk()
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        app = DynamicPricingEngine(root)
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        messagebox.showerror("Application Error", f"Failed to start the application: {str(e)}")


if __name__ == "__main__":
    main()
