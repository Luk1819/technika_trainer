import pandas as pd
import os
import json

# === KONFIGURATION ===
EXCEL_FILE = 'bauteile.xlsx'  # Deine Excel-Datei
OUTPUT_DART = 'part_database_generated.dart'  # Generierte Dart-Datei
OUTPUT_JSON = 'part_database.json'  # Optional: JSON für andere Zwecke
IMAGE_BASE_PATH = 'assets/images'  # Pfad zu den Bildern in der App

# Excel-Datei einlesen
print(f"Lese Excel-Datei: {EXCEL_FILE}")
try:
    # Lese die Excel-Datei, erste Zeile überspringen
    df = pd.read_excel(EXCEL_FILE, sheet_name=0, skiprows=1)
    
    # Setze die Spaltennamen manuell basierend auf der Struktur
    # Die Spalten sind: Teile-Nr, Name, Anzahl, Kasten-Nr, Fach
    if len(df.columns) >= 5:
        df.columns = ['TempCol0', 'Teile-Nr', 'Name', 'Anzahl', 'Kasten-Nr', 'Fach'][:len(df.columns)]
        # Entferne die erste temporäre Spalte falls vorhanden
        if 'TempCol0' in df.columns:
            df = df.drop(columns=['TempCol0'])
    
    # Entferne Zeilen wo Teile-Nr leer oder nicht numerisch ist
    df = df[df['Teile-Nr'].notna()]
    # Entferne Header-Zeilen (wo Teile-Nr der Text "Teile-Nr" ist)
    df = df[df['Teile-Nr'] != 'Teile-Nr']
    
except Exception as e:
    print(f"Fehler beim Lesen der Excel-Datei: {e}")
    import traceback
    traceback.print_exc()
    exit()

print(f"Gefunden: {len(df)} Einträge")
print(f"Spalten: {list(df.columns)}")
print()

# Spaltennamen normalisieren (falls sie Leerzeichen haben)
df.columns = df.columns.str.strip()

# Daten verarbeiten
parts_data = {}

for index, row in df.iterrows():
    try:
        # Konvertiere zu String und entferne .0 bei Ganzzahlen
        teile_nr_raw = row['Teile-Nr']
        if pd.notna(teile_nr_raw):
            # Wenn es eine Zahl ist, konvertiere zu int dann zu string (entfernt .0)
            if isinstance(teile_nr_raw, float):
                teile_nr = str(int(teile_nr_raw))
            else:
                teile_nr = str(teile_nr_raw).strip()
        else:
            continue  # Überspringe Zeilen ohne Teilenummer
            
        name = str(row['Name']).strip() if pd.notna(row['Name']) else 'Unbekannt'
        # Entferne Zeilenumbrüche aus dem Namen
        name = name.replace('\n', ' ').replace('\r', ' ')
        anzahl = int(row['Anzahl']) if pd.notna(row['Anzahl']) else 0
        kasten_nr = str(row['Kasten-Nr']).strip() if pd.notna(row['Kasten-Nr']) else ''
        # Kasten-Nr auch Ganzzahlen ohne .0
        if pd.notna(row['Kasten-Nr']) and isinstance(row['Kasten-Nr'], float):
            kasten_nr = str(int(row['Kasten-Nr']))
        fach = str(row['Fach']).strip() if pd.notna(row['Fach']) else ''
        
        # Bildpfad basierend auf Teilenummer
        image_path = f"{IMAGE_BASE_PATH}/{teile_nr}.png"
        
        # Kategorie aus Name ableiten (vereinfacht)
        category = 'Baustein'
        if 'strebe' in name.lower():
            category = 'Strebe'
        elif 'winkel' in name.lower():
            category = 'Winkelträger'
        elif 'riegel' in name.lower():
            category = 'Riegel'
        elif 'statik' in name.lower():
            category = 'Statik'
        
        # Teil-Daten zusammenstellen
        part_info = {
            'name': name,
            'description': f"{name} aus dem fischertechnik Sortiment.",
            'category': category,
            'technicalDetails': {
                'Teile-Nr': teile_nr,
                'Kasten': kasten_nr,
                'Fach': fach,
                'Anzahl verfügbar': str(anzahl),
            },
            'imagePath': image_path
        }
        
        parts_data[teile_nr] = part_info
        
    except Exception as e:
        print(f"Fehler bei Zeile {index}: {e}")
        continue

print(f"Verarbeitet: {len(parts_data)} Teile")

# === JSON AUSGABE (optional) ===
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(parts_data, f, indent=2, ensure_ascii=False)
print(f"JSON gespeichert: {OUTPUT_JSON}")

# === DART CODE GENERIEREN ===
dart_code = """// AUTOMATISCH GENERIERT - NICHT MANUELL BEARBEITEN
// Generiert aus: {excel_file}

class PartInfo {{
  final String name;
  final String description;
  final Map<String, String> technicalDetails;
  final String imagePath;
  final String category;

  PartInfo({{
    required this.name,
    required this.description,
    required this.technicalDetails,
    required this.imagePath,
    required this.category,
  }});

  // Statische Datenbank mit Teile-Informationen
  static final Map<String, PartInfo> partDatabase = {{
""".format(excel_file=EXCEL_FILE)

# Einträge hinzufügen
for teile_nr, info in parts_data.items():
    dart_code += f"    '{teile_nr}': PartInfo(\n"
    dart_code += f"      name: '{info['name']}',\n"
    dart_code += f"      category: '{info['category']}',\n"
    dart_code += f"      description: '{info['description']}',\n"
    dart_code += f"      technicalDetails: {{\n"
    for key, value in info['technicalDetails'].items():
        dart_code += f"        '{key}': '{value}',\n"
    dart_code += f"      }},\n"
    dart_code += f"      imagePath: '{info['imagePath']}',\n"
    dart_code += f"    ),\n"

# Abschluss mit getPartInfo Methode
dart_code += """  };

  static PartInfo? getPartInfo(String label) {
    // Versuche direktes Match
    if (partDatabase.containsKey(label)) {
      return partDatabase[label];
    }
    
    // Fallback: Nach Teilenummer im Label suchen
    for (var key in partDatabase.keys) {
      if (label.contains(key) || key.contains(label)) {
        return partDatabase[key];
      }
    }
    
    // Wenn nichts gefunden wurde, gebe ein Standard-Teil zurück
    return PartInfo(
      name: 'Unbekanntes Teil',
      category: 'Nicht klassifiziert',
      description: 'Dieses Teil wurde erkannt, ist aber noch nicht in der Datenbank.',
      technicalDetails: {
        'Erkanntes Label': label,
        'Hinweis': 'Bitte füge weitere Informationen zu diesem Teil hinzu.',
      },
      imagePath: 'assets/images/unknown.png',
    );
  }
}
"""

# Dart-Datei speichern
with open(OUTPUT_DART, 'w', encoding='utf-8') as f:
    f.write(dart_code)

print(f"Dart-Datei generiert: {OUTPUT_DART}")
print()
print("=== NÄCHSTE SCHRITTE ===")
print(f"1. Prüfe die generierte Datei: {OUTPUT_DART}")
print(f"2. Kopiere den Inhalt nach: technika_app/lib/models/part_info.dart")
print(f"3. Stelle sicher, dass alle Bilder in: technika_app/{IMAGE_BASE_PATH}/ liegen")
print(f"4. Bilder sollten benannt sein als: [Teile-Nr].png (z.B. 32064.png)")
