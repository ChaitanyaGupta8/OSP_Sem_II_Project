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

def add_flight_gui():
    top = tk.Toplevel(root)
    top.title("Add Flight")

    ttk.Label(top, text="Flight Number").pack()
    flight_number_entry = ttk.Entry(top)
    flight_number_entry.pack()

    ttk.Label(top, text="Origin").pack()
    origin_entry = ttk.Entry(top)
    origin_entry.pack()

    ttk.Label(top, text="Destination").pack()
    destination_entry = ttk.Entry(top)
    destination_entry.pack()

    ttk.Label(top, text="Total Seats").pack()
    seats_entry = ttk.Entry(top)
    seats_entry.pack()

    def submit_flight():
        try:
            total_seats = int(seats_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Total Seats must be a number.")
            return

        flight = {
            'id': generate_flight_id(),
            'flight_number': flight_number_entry.get(),
            'origin': origin_entry.get(),
            'destination': destination_entry.get(),
            'total_seats': total_seats,
            'available_seats': total_seats
        }
        flights.append(flight)
        save_data()
        messagebox.showinfo("Success", "Flight added successfully!")
        top.destroy()

    ttk.Button(top, text="Add Flight", command=submit_flight).pack(pady=10)

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
        messagebox.showwarning("No Flights", "No flights to book yet.")
        return

    options = [f"{f['flight_number']} ({f['id']})" for f in flights]
    selected = simpledialog.askstring("Book Ticket", "Choose Flight:\n" + "\n".join(options))
    if not selected:
        return

    selected_id = selected.split("(")[-1].strip(")")
    flight = next((f for f in flights if f['id'] == selected_id), None)

    if not flight:
        messagebox.showerror("Error", "Flight not found.")
        return

    if flight['available_seats'] <= 0:
        messagebox.showinfo("Full", "No seats available.")
        return

    name = simpledialog.askstring("Passenger Name", "Enter passenger name:")
    if not name:
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
    messagebox.showinfo("Success", "Ticket booked successfully!")

def view_bookings_gui():
    top = tk.Toplevel(root)
    top.title("View Bookings")

    if not bookings:
        ttk.Label(top, text="No bookings found.").pack()
        return

    for b in bookings:
        info = (
            f"Booking ID: {b['id']}\n"
            f"Passenger: {b['passenger_name']}\n"
            f"Flight Number: {b['flight_number']}\n"
            "-----------------------------"
        )
        ttk.Label(top, text=info, justify="left").pack(anchor="w", padx=10)

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


root = tk.Tk()
root.title("✈ Airline Management System")
root.geometry("500x700")
root.configure(bg="#f0f4f8")

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
main_frame.pack(expand=True)

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
root.mainloop()
