import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import uuid
import json
import os

# File paths
FLIGHT_FILE = "flights.json"
BOOKING_FILE = "bookings.json"

flights = []
bookings = []
USERNAME = "admin"
PASSWORD = "password"

def generate_flight_id():
    return "FL-" + str(uuid.uuid4())[:8]

def generate_booking_id():
    return "BK-" + str(uuid.uuid4())[:8]

def save_data():
    with open(FLIGHT_FILE, 'w') as f:
        json.dump(flights, f)
    with open(BOOKING_FILE, 'w') as f:
        json.dump(bookings, f)

def load_data():
    global flights, bookings
    if os.path.exists(FLIGHT_FILE):
        with open(FLIGHT_FILE, 'r') as f:
            flights = json.load(f)
    if os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, 'r') as f:
            bookings = json.load(f)


def login_gui():
    login_window = tk.Toplevel()
    login_window.title("🔐 Admin Login")
    login_window.geometry("400x260")
    login_window.resizable(False, False)
    center_window(login_window, 400, 260)
    login_window.grab_set()
    login_window.focus_force()

    style = ttk.Style()
    style.configure("Login.TEntry", padding=6, font=("Segoe UI", 11))
    style.configure("Login.TLabel", font=("Segoe UI", 11), background="#f0f4f8")
    style.configure("Login.TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.map("Login.TButton",
              background=[('active', '#004080'), ('!active', '#0059b3')],
              foreground=[('active', 'white'), ('!active', 'white')])

    frame = ttk.Frame(login_window, padding=20, style="TFrame")
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="✈ Admin Login", style="Header.TLabel").grid(columnspan=2, pady=(0, 20))

    ttk.Label(frame, text="👤 Username:", style="Login.TLabel").grid(row=1, column=0, sticky="e", padx=10, pady=8)
    username_entry = ttk.Entry(frame, width=25, style="Login.TEntry")
    username_entry.grid(row=1, column=1, pady=8)
    username_entry.focus()

    ttk.Label(frame, text="🔒 Password:", style="Login.TLabel").grid(row=2, column=0, sticky="e", padx=10, pady=8)
    password_entry = ttk.Entry(frame, show="*", width=25, style="Login.TEntry")
    password_entry.grid(row=2, column=1, pady=8)

    def check_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if username == USERNAME and password == PASSWORD:
            login_window.destroy()
            main_frame.pack(expand=True)
        else:
            messagebox.showerror("Login Failed", "❌ Invalid username or password.")

    login_window.bind('<Return>', lambda event: check_login())

    ttk.Button(frame, text="🔓 Login", style="Login.TButton", command=check_login).grid(row=3, columnspan=2, pady=20)

    

def center_window(win, width=400, height=300):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f'{width}x{height}+{x}+{y}')

def add_flight_gui():
    top = tk.Toplevel(root)
    top.title("➕ Add New Flight")
    center_window(top, 400, 350)

    frame = ttk.Frame(top, padding=15)
    frame.pack(expand=True, fill="both")

    labels = ["Flight Number", "Origin", "Destination", "Total Seats"]
    entries = {}

    for i, label in enumerate(labels):
        ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=10, pady=10)
        entry = ttk.Entry(frame)
        entry.grid(row=i, column=1, padx=10, pady=10)
        entries[label] = entry

    def submit_flight():
        flight_number = entries["Flight Number"].get().strip()
        origin = entries["Origin"].get().strip()
        destination = entries["Destination"].get().strip()
        seats = entries["Total Seats"].get().strip()

        if not all([flight_number, origin, destination, seats]):
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        try:
            total_seats = int(seats)
            if total_seats <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Total Seats must be a positive number.")
            return

        flight = {
            'id': generate_flight_id(),
            'flight_number': flight_number,
            'origin': origin,
            'destination': destination,
            'total_seats': total_seats,
            'available_seats': total_seats
        }
        flights.append(flight)
        save_data()
        messagebox.showinfo("Success", "✅ Flight added successfully!")
        top.destroy()

    ttk.Button(frame, text="Add Flight", command=submit_flight).grid(row=5, columnspan=2, pady=20)


def view_flights_gui():
    top = tk.Toplevel(root)
    top.title("View Flights")

    if not flights:
        ttk.Label(top, text="No flights available.").pack()
        return

    tree = ttk.Treeview(top, columns=("Number", "Origin", "Destination", "Seats"), show="headings")
    tree.heading("Number", text="Flight Number")
    tree.heading("Origin", text="Origin")
    tree.heading("Destination", text="Destination")
    tree.heading("Seats", text="Available/Total")
    tree.pack(fill="both", expand=True)

    for f in flights:
        tree.insert("", "end", values=(
            f["flight_number"],
            f["origin"],
            f["destination"],
            f"{f['available_seats']} / {f['total_seats']}"
        ))

def search_flights_gui():
    top = tk.Toplevel(root)
    top.title("Search Flights")

    frame = ttk.Frame(top, padding=10)
    frame.pack()

    ttk.Label(frame, text="Origin:").grid(row=0, column=0, sticky="e")
    origin_entry = ttk.Entry(frame)
    origin_entry.grid(row=0, column=1)

    ttk.Label(frame, text="Destination:").grid(row=1, column=0, sticky="e")
    destination_entry = ttk.Entry(frame)
    destination_entry.grid(row=1, column=1)

    result_box = tk.Text(top, height=10, wrap="word")
    result_box.pack(padx=10, pady=10, fill="both", expand=True)

    def search():
        origin = origin_entry.get().lower()
        destination = destination_entry.get().lower()
        result_box.delete("1.0", tk.END)

        matches = [f for f in flights if origin in f['origin'].lower() and destination in f['destination'].lower()]

        if matches:
            for f in matches:
                info = (
                    f"Flight Number: {f['flight_number']}\n"
                    f"From: {f['origin']} → {f['destination']}\n"
                    f"Seats: {f['available_seats']} / {f['total_seats']}\n"
                    "---------------------------\n"
                )
                result_box.insert(tk.END, info)
        else:
            result_box.insert(tk.END, "No flights found.")

    ttk.Button(frame, text="Search", command=search).grid(row=2, columnspan=2, pady=10)


def book_ticket_gui():
    if not flights:
        messagebox.showwarning("No Flights", "🚫 No flights available to book.")
        return

    top = tk.Toplevel(root)
    top.title("🎟 Book a Ticket")
    center_window(top, 420, 400)

    frame = ttk.Frame(top, padding=20)
    frame.pack(fill="both", expand=True)

    # Display all flights for reference
    flight_info_box = tk.Text(frame, height=8, width=50, wrap="word", state="normal")
    flight_info_box.grid(row=0, columnspan=2, padx=5, pady=10)

    flight_info_box.insert(tk.END, "📃 Available Flights:\n")
    for f in flights:
        flight_info_box.insert(tk.END,
            f"✈ {f['flight_number']} - {f['origin']} → {f['destination']} "
            f"({f['available_seats']} / {f['total_seats']} seats)\n"
        )
    flight_info_box.config(state="disabled")

    # Flight Number Entry
    ttk.Label(frame, text="Flight Number:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
    flight_number_entry = ttk.Entry(frame, width=30)
    flight_number_entry.grid(row=1, column=1, padx=10, pady=10)

    # Passenger Name Entry
    ttk.Label(frame, text="Passenger Name:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
    name_entry = ttk.Entry(frame, width=30)
    name_entry.grid(row=2, column=1, padx=10, pady=10)

    def book_ticket():
        flight_number = flight_number_entry.get().strip()
        name = name_entry.get().strip()

        if not flight_number or not name:
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return

        flight = next((f for f in flights if f['flight_number'].lower() == flight_number.lower()), None)

        if not flight:
            messagebox.showerror("Not Found", f"No flight found with number '{flight_number}'.")
            return

        if flight['available_seats'] <= 0:
            messagebox.showinfo("Full", f"❌ Flight {flight_number} has no available seats.")
            return

        booking = {
            'id': generate_booking_id(),
            'passenger_name': name,
            'flight_id': flight['id'],
            'flight_number': flight['flight_number']
        }

        bookings.append(booking)
        flight['available_seats'] -= 1
        save_data()
        messagebox.showinfo("Success", f"✅ Ticket booked for {name} on flight {flight_number}.")
        top.destroy()

    ttk.Button(frame, text="Book Ticket", command=book_ticket).grid(row=3, columnspan=2, pady=20)


def view_bookings_gui():
    top = tk.Toplevel(root)
    top.title("View Bookings")

    if not bookings:
        ttk.Label(top, text="No bookings found.").pack()
        return

    # Create a treeview widget with more structured columns
    tree = ttk.Treeview(top, columns=("Booking ID", "Passenger Name", "Flight Number"), show="headings")
    
    # Define headings for the columns
    tree.heading("Booking ID", text="Booking ID")
    tree.heading("Passenger Name", text="Passenger Name")
    tree.heading("Flight Number", text="Flight Number")

    # Allow sorting by each column
    tree.column("Booking ID", width=150, anchor="center")
    tree.column("Passenger Name", width=200, anchor="w")
    tree.column("Flight Number", width=150, anchor="center")
    
    tree.pack(fill="both", expand=True)

    # Insert all bookings into the treeview
    for b in bookings:
        tree.insert("", "end", values=(b['id'], b['passenger_name'], b['flight_number']))
    
    # Adding a button for better interaction (like cancelling a booking or deleting it)
    def cancel_selected():
        selected_item = tree.selection()
        if selected_item:
            booking_id = tree.item(selected_item)["values"][0]
            booking = next((b for b in bookings if b["id"] == booking_id), None)
            if booking:
                bookings.remove(booking)
                for f in flights:
                    if f['id'] == booking['flight_id']:
                        f['available_seats'] += 1
                        break
                save_data()
                tree.delete(selected_item)
                messagebox.showinfo("Success", "Booking cancelled successfully.")
            else:
                messagebox.showerror("Error", "Booking not found.")
        else:
            messagebox.showwarning("Select Booking", "Please select a booking to cancel.")

    ttk.Button(top, text="Cancel Selected Booking", command=cancel_selected).pack(pady=10)


def cancel_booking_gui():
    if not bookings:
        messagebox.showinfo("Info", "No bookings to cancel.")
        return

    top = tk.Toplevel(root)
    top.title("Cancel Booking")

    ttk.Label(top, text="Select Booking to Cancel:").pack(pady=5)
    listbox = tk.Listbox(top, width=50)
    for i, b in enumerate(bookings):
        listbox.insert(i, f"{b['passenger_name']} - {b['flight_number']} ({b['id']})")
    listbox.pack(pady=5)

    def cancel_selected():
        idx = listbox.curselection()
        if not idx:
            return
        booking = bookings.pop(idx[0])
        for f in flights:
            if f['id'] == booking['flight_id']:
                f['available_seats'] += 1
                break
        save_data()
        messagebox.showinfo("Success", "Booking cancelled.")
        top.destroy()

    ttk.Button(top, text="Cancel Booking", command=cancel_selected).pack(pady=5)

def delete_flight_gui():
    if not flights:
        messagebox.showinfo("Info", "No flights to delete.")
        return

    top = tk.Toplevel(root)
    top.title("Delete Flight")

    ttk.Label(top, text="Select Flight to Delete:").pack(pady=5)
    listbox = tk.Listbox(top, width=50)
    for i, f in enumerate(flights):
        listbox.insert(i, f"{f['flight_number']} - {f['origin']} → {f['destination']} ({f['id']})")
    listbox.pack(pady=5)

    def delete_selected():
        idx = listbox.curselection()
        if not idx:
            return
        flight = flights.pop(idx[0])
        global bookings
        bookings = [b for b in bookings if b['flight_id'] != flight['id']]
        save_data()
        messagebox.showinfo("Success", "Flight and associated bookings deleted.")
        top.destroy()

    ttk.Button(top, text="Delete Flight", command=delete_selected).pack(pady=5)

def view_passengers_gui():
    if not flights:
        messagebox.showinfo("Info", "No flights available.")
        return

    top = tk.Toplevel(root)
    top.title("View Passengers")

    ttk.Label(top, text="Select Flight:").pack(pady=5)
    listbox = tk.Listbox(top, width=50)
    for i, f in enumerate(flights):
        listbox.insert(i, f"{f['flight_number']} ({f['id']})")
    listbox.pack(pady=5)

    def show_passengers():
        idx = listbox.curselection()
        if not idx:
            return
        flight_id = flights[idx[0]]['id']
        passengers = [b['passenger_name'] for b in bookings if b['flight_id'] == flight_id]
        msg = "Passengers:\n" + "\n".join(passengers) if passengers else "No passengers booked."
        messagebox.showinfo("Passenger List", msg)

    ttk.Button(top, text="Show Passengers", command=show_passengers).pack(pady=5)


def toggle_theme(root, current_theme):
    if current_theme.get() == "light":
        root.configure(bg="#2e2e2e")
        current_theme.set("dark")
    else:
        root.configure(bg="#f0f0f0")
        current_theme.set("light")


def run_app():
    global root, main_frame

    root = tk.Tk()
    
    root.withdraw()  # Hide root until login is complete
    root.title("✈ Airline Management System")
    root.geometry("500x700")
    root.configure(bg="#f0f4f8")

    current_theme = tk.StringVar(value="light")
    toggle_button = ttk.Button(root, text="Toggle Theme", command=lambda: toggle_theme(root, current_theme))
    toggle_button.pack(pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f0f4f8")
    style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#003366")
    style.map("TButton",
              background=[('active', '#0059b3'), ('!active', '#0073e6')],
              foreground=[('active', 'white'), ('!active', 'white')])

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack_forget()  # Show only after login

    ttk.Label(main_frame, text="✈ Airline Management System ✈", style="Header.TLabel").pack(pady=(0, 20))

    buttons = [
        ("Add Flight", add_flight_gui),
        ("View Flights", view_flights_gui),
        ("Search Flights", search_flights_gui),
        ("Book Ticket", book_ticket_gui),
        ("View Bookings", view_bookings_gui),
        ("View Passengers", view_passengers_gui),
        ("Cancel Booking", cancel_booking_gui),
        ("Delete Flight", delete_flight_gui),
        ("Exit", lambda: (save_data(), root.quit()))
    ]

    for label, cmd in buttons:
        ttk.Button(main_frame, text=label, width=35, command=cmd).pack(pady=7)

    load_data()
    login_gui()  # Launch login as modal
    root.deiconify()  # Show main window after login window is closed
    root.mainloop()

run_app()

