import cv2
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import shutil

# --- KONFIGURATION ---
# Wichtig für PyInstaller: Pfad zur .exe verwenden, nicht zum temp-Ordner
if getattr(sys, 'frozen', False):
    # Läuft als .exe
    script_dir = os.path.dirname(sys.executable)
else:
    # Läuft als .py Script
    script_dir = os.path.dirname(os.path.abspath(__file__))

base_dir = os.path.join(script_dir, 'trainingsdaten')
classes_file = os.path.join(script_dir, 'classes.json')
# ---------------------

def load_classes():
    """Lädt die Klassenliste aus der JSON-Datei"""
    if os.path.exists(classes_file):
        with open(classes_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Standardklassen beim ersten Start
        default_classes = ['bauteil_a', 'bauteil_b', 'bauteil_c']
        save_classes(default_classes)
        return default_classes

def save_classes(classes):
    """Speichert die Klassenliste in einer JSON-Datei"""
    with open(classes_file, 'w', encoding='utf-8') as f:
        json.dump(classes, f, indent=2, ensure_ascii=False)

def get_image_count(class_name):
    """Zählt die Anzahl der Bilder im Ordner einer Klasse"""
    class_dir = os.path.join(base_dir, class_name)
    if not os.path.exists(class_dir):
        return 0
    # Zähle nur Bilddateien
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    count = sum(1 for f in os.listdir(class_dir) 
                if os.path.isfile(os.path.join(class_dir, f)) 
                and os.path.splitext(f)[1].lower() in image_extensions)
    return count

classes = load_classes()

def select_class_dialog(classes, current_class):
    """Zeigt ein Auswahlfenster mit Suchfunktion für Klassen"""
    selected_class = [current_class]  # Mutable container für Rückgabewert
    classes_modified = [False]  # Flag ob Klassen geändert wurden
    
    def on_select():
        selection = listbox.curselection()
        if selection:
            selected_class[0] = filtered_classes[selection[0]]
            dialog.destroy()
    
    def on_double_click(event):
        on_select()
    
    def filter_classes(*args):
        search_term = search_var.get().lower()
        filtered_classes.clear()
        listbox.delete(0, tk.END)
        
        for cls in classes:
            if search_term in cls.lower():
                filtered_classes.append(cls)
                listbox.insert(tk.END, cls)
        
        # Aktuelle Klasse hervorheben
        if selected_class[0] in filtered_classes:
            idx = filtered_classes.index(selected_class[0])
            listbox.selection_set(idx)
            listbox.see(idx)
    
    def add_class():
        new_class = simpledialog.askstring("Neue Klasse", "Name der neuen Klasse:", parent=dialog)
        if new_class:
            new_class = new_class.strip()
            if new_class and new_class not in classes:
                classes.append(new_class)
                classes.sort()  # Alphabetisch sortieren
                save_classes(classes)
                os.makedirs(os.path.join(base_dir, new_class), exist_ok=True)
                classes_modified[0] = True
                search_var.set("")  # Suche zurücksetzen
                filter_classes()
                messagebox.showinfo("Erfolg", f"Klasse '{new_class}' wurde hinzugefügt!", parent=dialog)
            elif new_class in classes:
                messagebox.showwarning("Fehler", "Diese Klasse existiert bereits!", parent=dialog)
    
    def delete_class():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine Klasse zum Löschen aus.", parent=dialog)
            return
        
        class_to_delete = filtered_classes[selection[0]]
        
        # Sicherheitsabfrage
        result = messagebox.askyesno(
            "Klasse löschen",
            f"Möchtest du die Klasse '{class_to_delete}' wirklich löschen?\n\n"
            f"ACHTUNG: Der gesamte Ordner mit allen Bildern wird gelöscht!",
            parent=dialog,
            icon='warning'
        )
        
        if result:
            # Ordner löschen
            class_dir = os.path.join(base_dir, class_to_delete)
            if os.path.exists(class_dir):
                shutil.rmtree(class_dir)
            
            # Klasse aus Liste entfernen
            classes.remove(class_to_delete)
            save_classes(classes)
            classes_modified[0] = True
            
            # Wenn gelöschte Klasse die aktuelle war, erste Klasse auswählen
            if selected_class[0] == class_to_delete:
                selected_class[0] = classes[0] if classes else None
            
            filter_classes()
            messagebox.showinfo("Erfolg", f"Klasse '{class_to_delete}' wurde gelöscht!", parent=dialog)
    
    # Dialog erstellen
    dialog = tk.Tk()
    dialog.title("Klasse auswählen")
    dialog.geometry("400x550")
    dialog.resizable(False, False)
    
    # Suchfeld
    search_frame = ttk.Frame(dialog, padding="10")
    search_frame.pack(fill=tk.X)
    
    ttk.Label(search_frame, text="Suche:").pack(side=tk.LEFT, padx=(0, 5))
    search_var = tk.StringVar()
    search_var.trace('w', filter_classes)
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    search_entry.focus()
    
    # Listbox mit Scrollbar
    list_frame = ttk.Frame(dialog, padding="10")
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 11))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    listbox.bind("<Double-Button-1>", on_double_click)
    
    # Verwaltungs-Buttons (Hinzufügen/Löschen)
    manage_frame = ttk.Frame(dialog, padding="10")
    manage_frame.pack(fill=tk.X)
    
    ttk.Button(manage_frame, text="➕ Neue Klasse", command=add_class).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(manage_frame, text="🗑️ Klasse löschen", command=delete_class).pack(side=tk.LEFT)
    
    # Auswahl-Buttons
    button_frame = ttk.Frame(dialog, padding="10")
    button_frame.pack(fill=tk.X)
    
    ttk.Button(button_frame, text="Auswählen", command=on_select).pack(side=tk.RIGHT)
    ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    
    # Initial befüllen
    filtered_classes = []
    filter_classes()
    
    # Enter-Taste zum Auswählen
    dialog.bind("<Return>", lambda e: on_select())
    dialog.bind("<Escape>", lambda e: dialog.destroy())
    
    dialog.mainloop()
    
    return selected_class[0], classes_modified[0]

for c in classes:
    os.makedirs(os.path.join(base_dir, c), exist_ok=True)

cap = cv2.VideoCapture(1)
current_class_idx = 0
count = get_image_count(classes[current_class_idx])  # Initiale Bildanzahl aus Ordner
auto_mode = False
frame_counter = 0

print(f"STEUERUNG:")
print(f"  [LEER] -> Einzelbild | [A] -> Auto-Modus AN/AUS")
print(f"  [K]    -> Klasse auswählen | [Q] -> Beenden")

while True:
    ret, frame = cap.read()
    if not ret: break

    current_class = classes[current_class_idx]
    frame_counter += 1

    # Logik für Auto-Modus: Alle 5 Frames ein Bild speichern
    if auto_mode and frame_counter % 5 == 0:
        img_name = f"{current_class}_auto_{time.time()}.jpg"
        cv2.imwrite(os.path.join(base_dir, current_class, img_name), frame)
        count = get_image_count(current_class)  # Aktualisiere Zähler

    # Visuelles Feedback im Fenster
    display_frame = frame.copy()
    status = "AUTO-REC" if auto_mode else "MANUELL"
    color = (0, 0, 255) if auto_mode else (0, 255, 0)
    
    cv2.putText(display_frame, f"KLASSE: {current_class}", (10, 30), 2, 0.8, (255, 255, 255), 2)
    cv2.putText(display_frame, f"MODUS: {status} | Bilder: {count}", (10, 60), 2, 0.8, color, 2)
    cv2.imshow('Data Collector Pro', display_frame)

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '): # Einzelbild
        cv2.imwrite(os.path.join(base_dir, current_class, f"{current_class}_{time.time()}.jpg"), frame)
        count = get_image_count(current_class)  # Aktualisiere Zähler
    elif key == ord('a'): # Auto-Modus togglen
        auto_mode = not auto_mode
    elif key == ord('k'): # Klasse über Dialog auswählen
        auto_mode = False  # Auto-Modus zur Sicherheit aus
        selected, modified = select_class_dialog(classes, current_class)
        if modified:
            classes = load_classes()  # Aktualisierte Klassen neu laden
        if selected and selected in classes:
            current_class_idx = classes.index(selected)
            count = get_image_count(classes[current_class_idx])  # Aktualisiere Zähler für neue Klasse
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()