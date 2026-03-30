# Automatische Übersetzung der part_database.json

## 🎯 Zweck

Das Script `translate_database.py` konvertiert deine `part_database.json` automatisch von:

**String-Format** (nur Deutsch):
```json
{
  "32064": {
    "name": "Baustein 15 mit Bohrung",
    "description": "Baustein 15 mit Bohrung..."
  }
}
```

**Multi-Language-Format** (mehrere Sprachen):
```json
{
  "32064": {
    "name": {
      "de": "Baustein 15 mit Bohrung",
      "en": "Building Block 15 with Bore",
      "fr": "Bloc de construction 15 avec alésage"
    },
    "description": {
      "de": "Baustein 15 mit Bohrung...",
      "en": "Building block 15 with bore...",
      "fr": "Bloc de construction 15..."
    }
  }
}
```

---

## 📦 Installation

### Schritt 1: Python Dependencies installieren

**Option A: Google Translate (Empfohlen für Einstieg)**
```bash
pip install googletrans==4.0.0-rc1
```

**Option B: DeepL (Beste Qualität)**
```bash
pip install deepl
```
→ Benötigt API Key von https://www.deepl.com/pro-api

**Option C: OpenAI (Sehr gut)**
```bash
pip install openai
```
→ Benötigt API Key von https://platform.openai.com/api-keys

---

## 🚀 Verwendung

### Basis-Verwendung (Google Translate, nur Englisch)

```bash
python translate_database.py
```

Dies erstellt `part_database_multilang.json` mit Englisch-Übersetzungen.

---

### Mehrere Sprachen übersetzen

```bash
python translate_database.py --languages en fr es it
```

Übersetzt nach Englisch, Französisch, Spanisch und Italienisch.

---

### DeepL verwenden (bessere Qualität)

1. API Key in `translate_database.py` einfügen:
   ```python
   DEEPL_API_KEY = "dein-api-key-hier"
   ```

2. Ausführen:
   ```bash
   python translate_database.py --translator deepl --languages en fr
   ```

---

### Mit Backup der Original-Datei

```bash
python translate_database.py --backup
```

Erstellt `part_database.json.backup` vor der Übersetzung.

---

### Spezifische Ein- und Ausgabe-Dateien

```bash
python translate_database.py \
  --input ../technika_app/assets/part_database.json \
  --output ../technika_app/assets/part_database.json \
  --backup \
  --languages en fr
```

---

## 📋 Alle Optionen

```bash
python translate_database.py --help
```

| Option | Beschreibung | Standard |
|--------|--------------|----------|
| `--input`, `-i` | Eingabe-Datei | `part_database.json` |
| `--output`, `-o` | Ausgabe-Datei | `part_database_multilang.json` |
| `--translator`, `-t` | Service (`google`, `deepl`, `openai`) | `google` |
| `--languages`, `-l` | Ziel-Sprachen | `en` |
| `--backup`, `-b` | Backup erstellen | Nein |

---

## 🌍 Unterstützte Sprachen

ISO 639-1 Sprachcodes:

- `en` - English
- `fr` - Français
- `es` - Español
- `it` - Italiano
- `pt` - Português
- `nl` - Nederlands
- `pl` - Polski
- `ru` - Русский
- `ja` - 日本語
- `zh` - 中文

---

## 💡 Empfohlener Workflow

### 1. Test mit wenigen Teilen

Erstelle eine Test-JSON mit 5-10 Teilen:
```bash
python translate_database.py --input test_sample.json --languages en
```

Prüfe die Qualität der Übersetzungen.

### 2. Volle Übersetzung

```bash
python translate_database.py \
  --input ../technika_app/assets/part_database.json \
  --output ../technika_app/assets/part_database_new.json \
  --backup \
  --translator google \
  --languages en fr
```

### 3. Manuelle Prüfung

Öffne `part_database_new.json` und prüfe stichprobenartig die Übersetzungen.

### 4. Ersetzen & Testen

```bash
# Backup erstellen (zur Sicherheit)
cp ../technika_app/assets/part_database.json ../technika_app/assets/part_database.json.old

# Neue Datei verwenden
cp ../technika_app/assets/part_database_new.json ../technika_app/assets/part_database.json
```

### 5. Datenbankversion erhöhen

In `lib/services/database_version_manager.dart`:
```dart
static const int currentVersion = 8; // +1
```

### 6. App testen

```bash
cd ../technika_app
flutter run
```

---

## ⚠️ Wichtige Hinweise

### Qualität der Übersetzungen

- **Google Translate**: Schnell, kostenlos, aber manchmal ungenau (besonders bei Fachbegriffen)
- **DeepL**: Sehr gut für europäische Sprachen, kostenpflichtig
- **OpenAI**: Sehr gut, versteht Kontext besser, kostenpflichtig

**Empfehlung**: 
1. Teste mit Google Translate
2. Für Produktion: Verwende DeepL oder überprüfe manuell

### Kosten

- **Google Translate (googletrans)**: Kostenlos (nutzt inoffizielle API)
- **DeepL**: Free Tier 500.000 Zeichen/Monat, dann ca. 5€/Million Zeichen
- **OpenAI**: ca. 0.0005-0.002$ pro 1000 Zeichen

### Rate Limits

Bei großen Datenbanken (>1000 Teile):
- Füge Pausen ein (kannst du im Script anpassen)
- Verwende DeepL oder OpenAI mit offiziellem API Key

### Fehlerbehandlung

Das Script:
- ✅ Behält Original-Daten bei Übersetzungsfehlern
- ✅ Zeigt Fortschritt für jedes Teil
- ✅ Erstellt vollständige Statistik am Ende

---

## 🔧 Anpassungen

### API Keys als Umgebungsvariablen

Statt API Keys im Script zu speichern:

```python
# Am Anfang von translate_database.py ändern:
import os
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

Dann:
```bash
export DEEPL_API_KEY="dein-key"
python translate_database.py --translator deepl
```

### Eigene Quellsprache

Im Script ändern:
```python
SOURCE_LANGUAGE = 'en'  # Wenn deine JSON auf Englisch ist
```

---

## 📊 Beispiel-Output

```
📂 Lade part_database.json...
💾 Erstelle Backup: part_database.json.backup

🔧 Initialisiere GOOGLE Übersetzer...

🌍 Starte Übersetzung von 3857 Teilen...
Quellsprache: de
Zielsprachen: en, fr

[1/3857] Teil 32064... ✅
[2/3857] Teil 32321... ✅
[3/3857] Teil 32881... ✅
...

💾 Speichere Ergebnis in part_database_multilang.json...

==================================================
📊 Übersetzungs-Statistik
==================================================
Gesamt Teile:       3857
Erfolgreich:        3857 ✅
Fehler:             0 ❌
==================================================

✨ Fertig! Übersetzte Datei: part_database_multilang.json

⚠️  WICHTIG: Prüfe die Übersetzungen manuell!
⚠️  Erhöhe danach die Datenbankversion in database_version_manager.dart
```

---

## 🤔 Troubleshooting

### "googletrans ImportError"
```bash
pip uninstall googletrans
pip install googletrans==4.0.0-rc1
```

### "DeepL quota exceeded"
→ Du hast das kostenlose Limit überschritten. Warte bis nächsten Monat oder upgrade.

### "OpenAI RateLimitError"
→ Zu viele Anfragen. Füge Pausen hinzu oder erhöhe dein OpenAI Limit.

### Schlechte Übersetzungen
→ Verwende DeepL oder überprüfe/korrigiere manuell wichtige Teile.

---

## 📝 Lizenz

Dieses Script ist Teil der Technika App. Verwende es frei für dein Projekt!
