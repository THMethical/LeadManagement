import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

# MySQL-Verbindung
def connect_to_db():
    return mysql.connector.connect(
        host="#",
        port=3306,
        user="#",
        password="#",
        database="#"
    )

def initialize_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        unternehmensname VARCHAR(255),
                        kontaktperson VARCHAR(255),
                        telefon VARCHAR(255),
                        email VARCHAR(255),
                        angebotene_produkte VARCHAR(255),
                        kontaktstatus VARCHAR(50),
                        budget VARCHAR(50),
                        letzte_kontaktaufnahme DATE,
                        notizen TEXT
                      )''')
    conn.commit()
    conn.close()

def save_to_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO leads (
                        unternehmensname, kontaktperson, telefon, email, angebotene_produkte, kontaktstatus, budget, letzte_kontaktaufnahme, notizen
                      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (entry_company.get(), entry_contact.get(), entry_phone.get(), entry_email.get(), combo_products.get(),
                    combo_status.get(), combo_budget.get(), date_contact.get_date(), text_notes.get("1.0", tk.END)))
    conn.commit()
    conn.close()
    messagebox.showinfo("Erfolg", "Daten wurden erfolgreich gespeichert.")
    update_treeview()
    clear_entries()

def update_treeview():
    for row in tree.get_children():
        tree.delete(row)

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()

def on_item_select(event):
    selected_item = tree.focus()
    values = tree.item(selected_item, "values")

    if values:
        clear_entries()

        entry_company.insert(0, values[1])
        entry_contact.insert(0, values[2])
        entry_phone.insert(0, values[3])
        entry_email.insert(0, values[4])
        combo_products.set(values[5])
        combo_status.set(values[6])
        combo_budget.set(values[7])
        
        # Setze das Datum nur, wenn es nicht leer ist
        if values[8] and values[8] != 'None':
            date_contact.set_date(values[8])
        
        text_notes.delete("1.0", tk.END)
        text_notes.insert(tk.END, values[9])

def update_entry():
    selected_item = tree.focus()
    values = tree.item(selected_item, "values")
    if not values:
        messagebox.showerror("Fehler", "Kein Eintrag ausgewählt.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''UPDATE leads SET 
                        unternehmensname=%s, kontaktperson=%s, telefon=%s, email=%s, angebotene_produkte=%s, 
                        kontaktstatus=%s, budget=%s, letzte_kontaktaufnahme=%s, notizen=%s
                      WHERE id=%s''',
                   (entry_company.get(), entry_contact.get(), entry_phone.get(), entry_email.get(), combo_products.get(),
                    combo_status.get(), combo_budget.get(), date_contact.get_date(), text_notes.get("1.0", tk.END), values[0]))
    conn.commit()
    conn.close()
    messagebox.showinfo("Erfolg", "Daten wurden erfolgreich aktualisiert.")
    update_treeview()

def delete_entry():
    selected_item = tree.focus()
    values = tree.item(selected_item, "values")
    if not values:
        messagebox.showerror("Fehler", "Kein Eintrag ausgewählt.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id=%s", (values[0],))
    conn.commit()
    conn.close()
    messagebox.showinfo("Erfolg", "Daten wurden erfolgreich gelöscht.")
    update_treeview()

def clear_entries():
    entry_company.delete(0, tk.END)
    entry_contact.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    combo_products.set('')
    combo_status.set('')
    combo_budget.set('')
    # Nur ein leeres Datum, wenn es bereits gesetzt ist
    if date_contact.get():
        date_contact.set_date(None)
    text_notes.delete("1.0", tk.END)

# Hauptfenster
app = tk.Tk()
app.title("Lead Management Tool")
app.geometry("750x600")
app.configure(bg="#f4f4f4")

# Stil definieren
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12), background="#f4f4f4")
style.configure("TEntry", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12), background="#007bff", foreground="white", padding=6)
style.map("TButton", background=[('active', '#0056b3')])
style.configure("TFrame", background="#f4f4f4")
style.configure("TLabelframe", background="#e9ecef", padding=10)

# Notebook für Tabs
notebook = ttk.Notebook(app)
notebook.pack(pady=10, expand=True, fill="both")

# Tab 1 - Lead-Daten
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Lead-Daten")

# Formular
form_frame = ttk.LabelFrame(tab1, text="Lead-Daten", padding=(10, 5))
form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

labels = ["Unternehmensname", "Kontaktperson", "Telefon", "E-Mail", "Angebotene Produkte", "Kontaktstatus", "Budget", "Letzte Kontaktaufnahme", "Notizen"]
entries = []

# Eingabefelder und Dropdowns
entry_company = ttk.Entry(form_frame, font=("Arial", 12))
entry_contact = ttk.Entry(form_frame, font=("Arial", 12))
entry_phone = ttk.Entry(form_frame, font=("Arial", 12))
entry_email = ttk.Entry(form_frame, font=("Arial", 12))
combo_products = ttk.Combobox(form_frame, values=["Produkt A", "Produkt B", "Produkt C"], font=("Arial", 12))
combo_status = ttk.Combobox(form_frame, values=["Erstkontakt", "Interessiert", "Angebot geschickt", "Abschluss", "Kein Interesse"], font=("Arial", 12))
combo_budget = ttk.Combobox(form_frame, values=["< 1000€", "1000€ - 5000€", "5000€ - 10000€", "> 10000€"], font=("Arial", 12))
date_contact = DateEntry(form_frame, font=("Arial", 12), date_pattern='dd/mm/yyyy')
text_notes = tk.Text(form_frame, font=("Arial", 12), height=4, width=50)

for i, label_text in enumerate(labels):
    label = ttk.Label(form_frame, text=label_text)
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    widget = None
    if label_text == "Kontaktstatus":
        widget = combo_status
    elif label_text == "Budget":
        widget = combo_budget
    elif label_text == "Letzte Kontaktaufnahme":
        widget = date_contact
    elif label_text == "Notizen":
        widget = text_notes
    elif label_text == "Angebotene Produkte":
        widget = combo_products
    else:
        widget = entry_company if label_text == "Unternehmensname" else (
                entry_contact if label_text == "Kontaktperson" else (
                entry_phone if label_text == "Telefon" else (
                entry_email)))

    widget.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

# Buttons
button_frame = ttk.Frame(form_frame)
button_frame.grid(row=len(labels), columnspan=2, pady=10, sticky="ew")

buttons = {
    "Speichern": save_to_db,
    "Aktualisieren": update_entry,
    "Löschen": delete_entry,
    "Felder leeren": clear_entries
}

for i, (text, command) in enumerate(buttons.items()):
    button = ttk.Button(button_frame, text=text, command=command)
    button.grid(row=0, column=i, padx=5)

# Tab 2 - Datenbankansicht
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Datenbankansicht")

# Scrollbares Treeview
tree_frame = ttk.Frame(tab2)
tree_frame.pack(pady=10, expand=True, fill="both")

# Treeview und Scrollbars
tree = ttk.Treeview(tree_frame, columns=("id", "unternehmen", "kontaktperson", "telefon", "email", "produkte", "status", "budget", "kontaktaufnahme", "notizen"), show="headings")
tree.heading("id", text="ID")
tree.heading("unternehmen", text="Unternehmen")
tree.heading("kontaktperson", text="Kontaktperson")
tree.heading("telefon", text="Telefon")
tree.heading("email", text="E-Mail")
tree.heading("produkte", text="Produkte")
tree.heading("status", text="Status")
tree.heading("budget", text="Budget")
tree.heading("kontaktaufnahme", text="Kontaktaufnahme")
tree.heading("notizen", text="Notizen")
tree.bind("<ButtonRelease-1>", on_item_select)

vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
vsb.pack(side='right', fill='y')
tree.configure(yscrollcommand=vsb.set)

hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
hsb.pack(side='bottom', fill='x')
tree.configure(xscrollcommand=hsb.set)

tree.pack(fill="both", expand=True)

update_treeview()

app.mainloop()
