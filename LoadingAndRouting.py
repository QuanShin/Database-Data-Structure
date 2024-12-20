import math
import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


# TSP Route Calculation Functions
def euclidean_distance(coord1, coord2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)
def generate_distance_matrix_from_coordinates(cities, coordinates):
    n = len(cities)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            matrix[i][j] = euclidean_distance(coordinates[cities[i]], coordinates[cities[j]])
    return matrix

def tsp_greedy_with_distances(city_distances, cities):
    visited = set()
    route = ["Hanoi"]  # Start in Hanoi
    while len(route) < len(cities):
        next_city = min(
            (city for city in cities if city not in visited),
            key=lambda city: city_distances.get(city, float('inf'))
        )
        route.append(next_city)
        visited.add(next_city)

    if route[-1] != "Hanoi":
        route.append("Hanoi")  # Return to Hanoi
    return route

# Truck Management Application
class Package:
    def __init__(self, package_code, location, weight, distance, shipping_type, payment_status="Unpaid"):
        self.package_code = package_code
        self.location = location
        self.weight = weight
        self.distance = distance
        self.shipping_type = shipping_type
        self.payment_status = payment_status


class TruckApp:
    def __init__(self, root):
        self.root = root
        self.max_weight = 25
        self.packages = []
        self.trucks = []
        self.generated_codes = set()

        # City coordinates for TSP
        self.city_coordinates = {
            "Hanoi": (21.0285, 105.8542),
            "Da Nang": (16.0471, 108.2068),
            "HCMC": (10.8231, 106.6297),
            "Nha Trang": (12.2388, 109.1967),
            "Dalat": (11.9404, 108.4583),
            "Hai Phong": (20.8449, 106.6881),
        }

        self.packages = self.generate_packages()
        self.trucks = self.allocate_trucks()
        self.setup_ui()

    # Other methods (generate_random_code, generate_packages, knapsack, etc.) remain unchanged...
    def generate_random_code(self):
        """Generate a unique 6-character alphanumeric package code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if code not in self.generated_codes:
                self.generated_codes.add(code)
                return code

    def generate_packages(self):
        locations = [
            {"city": "Da Nang", "distance": 767},
            {"city": "HCMC", "distance": 1750},
            {"city": "Nha Trang", "distance": 1300},
            {"city": "Dalat", "distance": 1480},
            {"city": "Hai Phong", "distance": 120},
        ]

        shipping_types = ["COD", "Bank Transfer", "Credit Card"]
        packages = []
        for i in range(6):
            loc = random.choice(locations)
            shipping_type = random.choice(shipping_types)
            payment_status = "Pay later (COD)" if shipping_type == "COD" else "Unpaid"
            packages.append(Package(
                package_code=f"P{random.randint(100000, 999999)}",
                location=loc["city"],
                weight=random.randint(1, 10),
                distance=loc["distance"],
                shipping_type=shipping_type,
                payment_status=payment_status
            ))
        return packages
        

    def knapsack(self, packages):
        n = len(packages)
        dp = [[0] * (self.max_weight + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(self.max_weight + 1):
                dp[i][w] = dp[i - 1][w]
                if packages[i - 1].weight <= w:
                    dp[i][w] = max(dp[i][w], dp[i - 1][w - packages[i - 1].weight] + packages[i - 1].weight)

        truck = []
        w = self.max_weight
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                truck.append(packages[i - 1])
                w -= packages[i - 1].weight

        remaining_packages = [p for p in packages if p not in truck]
        truck.sort(key=lambda p: p.distance, reverse=True)

        return truck, remaining_packages

    def allocate_trucks(self):
        # Allocate packages to trucks using the knapsack algorithm
        allocated_trucks = []
        remaining_packages = self.packages

        while remaining_packages:
            truck, remaining_packages = self.knapsack(remaining_packages)
            allocated_trucks.append(truck)

        # Sort trucks by the furthest destination (max distance in each truck)
        allocated_trucks.sort(key=lambda truck: max(package.distance for package in truck), reverse=True)
        return allocated_trucks


    def setup_ui(self):
        self.root.title("Truck Management")
        self.root.geometry("1000x1000")
        self.package_table = ttk.Treeview(self.root, columns=("Code", "Location", "Weight", "Distance", "Shipping Type", "Payment Status"), show="headings")
        for col in ["Code", "Location", "Weight", "Distance", "Shipping Type", "Payment Status"]:
            self.package_table.heading(col, text=col)
            self.package_table.column(col, width=150)  # Adjust column width for better readability
        self.package_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Package", command=self.add_package).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Cancel Package", command=self.cancel_package).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Confirm Payment", command=self.confirm_payment).grid(row=0, column=2, padx=5)

        # Truck list
        self.truck_dropdown = ttk.Treeview(self.root, columns=["Truck"], show="headings")
        self.truck_dropdown.heading("Truck", text="Truck List")
        self.truck_dropdown.column("Truck", width=300)  # Adjust column width
        self.truck_dropdown.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.truck_dropdown.bind("<<TreeviewSelect>>", self.display_truck)

        tk.Button(self.root, text="Generate Invoice", command=self.generate_invoice).pack(pady=5)
        tk.Button(self.root, text="Generate TSP Route", command=self.generate_tsp_route).pack(pady=5)
        tk.Button(self.root, text="Backup Route", command=self.show_backup_route).pack(pady=5)



        # Truck display table
        self.truck_table = ttk.Treeview(self.root, columns=("Code", "Location", "Weight", "Distance", "Shipping Type", "Payment Status"), show="headings")
        for col in ["Code", "Location", "Weight", "Distance", "Shipping Type", "Payment Status"]:
            self.truck_table.heading(col, text=col)
            self.truck_table.column(col, width=150)  # Adjust column width for better readability
        self.truck_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_package_table()
        self.update_truck_list()

        # Package table setup
        # (Code for UI setup remains unchanged)

        # Add Generate TSP Route button

    def generate_tsp_route(self):
        selected_item = self.truck_dropdown.selection()
        if not selected_item:
            messagebox.showerror("Error", "No truck selected.")
            return

        truck_index = int(self.truck_dropdown.item(selected_item)["values"][0].split()[-1]) - 1
        truck_packages = self.trucks[truck_index]

        # Extract the cities and distances for the selected truck's packages
        truck_cities = list({pkg.location for pkg in truck_packages})  # Unique cities only
        if "Hanoi" not in truck_cities:
            truck_cities.insert(0, "Hanoi")  # Ensure Hanoi is the start

        # Retrieve distances from packages
        city_distances = {pkg.location: pkg.distance for pkg in truck_packages}

        # Generate the TSP route using distances
        optimized_route = tsp_greedy_with_distances(city_distances, truck_cities)

        # Display the optimized route
        route_window = tk.Toplevel(self.root)
        route_window.title("Optimized TSP Route")
        route_window.geometry("400x400")
        tk.Label(route_window, text="Optimized Delivery Route", font=("Arial", 14, "bold")).pack(pady=10)
        for city in optimized_route:
            tk.Label(route_window, text=city).pack(anchor="w", padx=10)

        tk.Button(route_window, text="Close", command=route_window.destroy).pack(pady=10)

    def show_backup_route(self):
        # Ensure a truck is selected
        selected_item = self.truck_dropdown.selection()
        if not selected_item:
            messagebox.showerror("Error", "No truck selected.")
            return

        truck_index = int(self.truck_dropdown.item(selected_item)["values"][0].split()[-1]) - 1
        truck_packages = self.trucks[truck_index]

        # Extract unique cities from truck packages
        truck_cities = list({pkg.location for pkg in truck_packages})

        if not truck_cities:
            messagebox.showwarning("No Cities", "No cities assigned to the selected truck.")
            return

        # Ensure all city coordinates are available
        missing_coords = [city for city in truck_cities if city not in self.city_coordinates]
        if missing_coords:
            messagebox.showerror("Error", f"Missing coordinates for: {', '.join(missing_coords)}")
            return

        # Start from Hanoi
        current_city = "Hanoi"
        route = [current_city]
        unvisited_cities = set(truck_cities)

        # Calculate route based on nearest neighbor (greedy)
        while unvisited_cities:
            next_city = min(
                unvisited_cities,
                key=lambda city: euclidean_distance(self.city_coordinates[current_city], self.city_coordinates[city])
            )
            route.append(next_city)
            current_city = next_city
            unvisited_cities.remove(next_city)

        # Return to Hanoi
        route.append("Hanoi")

        # Display the route in a new window
        route_window = tk.Toplevel(self.root)
        route_window.title("Backup Delivery Route")
        route_window.geometry("400x400")
        tk.Label(route_window, text="Backup Route (Euclidean Distance)", font=("Arial", 14, "bold")).pack(pady=10)

        for city in route:
            tk.Label(route_window, text=f"→ {city}").pack(anchor="w", padx=10)

        tk.Button(route_window, text="Close", command=route_window.destroy).pack(pady=10)

    def update_package_table(self):
        # Clear the package table
        for row in self.package_table.get_children():
            self.package_table.delete(row)

        # Add updated data to the package table
        for package in self.packages:
            self.package_table.insert("", "end", values=(
                package.package_code,
                package.location,
                package.weight,
                package.distance,
                package.shipping_type,
                package.payment_status  # Ensure Payment Status is displayed
            ))
        self.package_table.update_idletasks()


    def update_truck_list(self):
        # Clear the previous truck list display
        for row in self.truck_dropdown.get_children():
            self.truck_dropdown.delete(row)

        # Sort trucks by the furthest package inside each truck
        sorted_trucks = sorted(enumerate(self.trucks), key=lambda x: x[1][0].distance if x[1] else 0, reverse=True)

        # Insert trucks in sorted order based on the furthest package
        for i, truck in sorted_trucks:
            self.truck_dropdown.insert("", "end", values=(f"Truck {i+1}",))

        # Display truck packages in the truck table for the first truck
        self.display_truck(None)

    def display_truck(self, event):
        selected_item = self.truck_dropdown.selection()
        if not selected_item:
            return

        # Get the truck number from the selected row
        truck_index = int(self.truck_dropdown.item(selected_item)["values"][0].split()[-1]) - 1
        truck_packages = self.trucks[truck_index]

        # Clear existing rows in the truck display table
        for row in self.truck_table.get_children():
            self.truck_table.delete(row)

        # Insert packages of the selected truck, including Payment Type and Payment Status
        for package in truck_packages:
            self.truck_table.insert("", "end", values=(
                package.package_code,
                package.location,
                package.weight,
                package.distance,
                package.shipping_type,
                package.payment_status  # Display Payment Status
            ))
        self.package_table.update_idletasks()


    def add_package(self):
        # Open a new window for package addition
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Package")
        add_window.geometry("400x400")

        tk.Label(add_window, text="Weight (1-10):").pack(pady=5)
        weight_entry = tk.Entry(add_window)
        weight_entry.pack(pady=5)

        tk.Label(add_window, text="Destination:").pack(pady=5)
        destination_var = tk.StringVar()
        destination_dropdown = ttk.Combobox(add_window, textvariable=destination_var, values=["HCMC", "Nha Trang", "Da Nang", "Dalat", "Hai Phong"])
        destination_dropdown.pack(pady=5)

        tk.Label(add_window, text="Payment Type:").pack(pady=5)
        payment_type_var = tk.StringVar()
        payment_type_dropdown = ttk.Combobox(add_window, textvariable=payment_type_var, values=["COD", "Bank Transfer", "Credit Card"])
        payment_type_dropdown.pack(pady=5)

        def confirm_add():
            try:
                weight = int(weight_entry.get())
                if weight < 1 or weight > 10:
                    raise ValueError("Invalid weight")
                destination = destination_var.get()
                if destination not in ["HCMC", "Nha Trang", "Da Nang", "Dalat", "Hai Phong"]:
                    raise ValueError("Invalid destination")
                payment_type = payment_type_var.get()
                if payment_type not in ["COD", "Bank Transfer", "Credit Card"]:
                    raise ValueError("Invalid payment type")
                
                # Set the payment status based on the payment type
                payment_status = "Pay later (COD)" if payment_type == "COD" else "Unpaid"
                
                # Generate a random unique code for the package
                package_code = self.generate_random_code()

                # Create the new package
                new_package = Package(
                    package_code, 
                    destination, 
                    weight, 
                    random.randint(500, 2000),
                    payment_type,
                    payment_status
                )
                self.packages.append(new_package)
                
                # Update trucks and UI
                self.trucks = self.allocate_trucks()
                self.update_package_table()
                self.update_truck_list()

                messagebox.showinfo("Success", f"Package {new_package.package_code} added successfully.")
                add_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        tk.Button(add_window, text="Add", command=confirm_add).pack(pady=10)
        tk.Button(add_window, text="Cancel", command=add_window.destroy).pack(pady=5)
    
    def cancel_package(self):
        selected_item = self.package_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No package selected to cancel")
            return

        # Get the selected package's index
        package_index = self.package_table.index(selected_item[0])
        canceled_package = self.packages[package_index]

        # Remove the package and its code from tracking
        del self.packages[package_index]
        self.generated_codes.discard(canceled_package.package_code)

        # Reallocate packages and update truck list
        self.trucks = self.allocate_trucks()
        self.update_package_table()
        self.update_truck_list()

        # Success message
        messagebox.showinfo("Success", f"Package {canceled_package.package_code} has been successfully canceled.")

    def confirm_payment(self):
        selected_item = self.package_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No package selected for payment confirmation.")
            return

        package_index = self.package_table.index(selected_item[0])
        package = self.packages[package_index]

        if package.payment_status == "Pay later (COD)":  # COD payments are automatically valid
            messagebox.showinfo("Info", f"Package {package.package_code} is already set as Pay later (COD).")
        elif package.shipping_type == "COD":
            package.payment_status = "Pay later (COD)"
        else:
            package.payment_status = "Paid"

        self.update_package_table()
        self.update_truck_list()
        messagebox.showinfo("Success", f"Package {package.package_code} payment confirmed.")
    
    def generate_invoice(self):
        # Validate the selected truck
        selected_item = self.truck_dropdown.selection()
        if not selected_item:
            messagebox.showerror("Error", "No truck selected.")
            return

        # Get the selected truck
        truck_index = int(self.truck_dropdown.item(selected_item)["values"][0].split()[-1]) - 1
        truck_packages = self.trucks[truck_index]

        # Check if all packages are Paid or Pay later (COD)
        unpaid_packages = [p for p in truck_packages if p.payment_status not in ("Paid", "Pay later (COD)")]
        if unpaid_packages:
            unpaid_codes = ", ".join(p.package_code for p in unpaid_packages)
            messagebox.showerror("Error", f"Cannot generate invoice. Unpaid packages: {unpaid_codes}")
            return

        # Calculate the cost for each package and the total
        package_costs = [
            (p.package_code, p.location, (p.weight * p.distance * 0.05) + 100)
            for p in truck_packages
        ]
        total_cost = sum(cost for _, _, cost in package_costs)

        # Display the invoice in a new pop-up window
        invoice_window = tk.Toplevel(self.root)
        invoice_window.title("Invoice")
        invoice_window.geometry("500x500")

        # Title of the Invoice
        tk.Label(invoice_window, text=f"Invoice for Truck {truck_index + 1}", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(invoice_window, text="Packages Included:", font=("Arial", 12)).pack(pady=5)

        # Display each package's details
        for package_code, location, cost in package_costs:
            tk.Label(invoice_window, text=f"Code: {package_code}, Delivered to: {location}, Cost: ${cost:.2f}").pack(anchor="w", padx=10)

        # Display the total cost
        tk.Label(invoice_window, text=f"Total Cost: ${total_cost:.2f}", font=("Arial", 12, "bold")).pack(pady=20)

        # Close button
        tk.Button(invoice_window, text="Close", command=invoice_window.destroy).pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    app = TruckApp(root)
    root.mainloop()
