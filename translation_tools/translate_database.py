#!/usr/bin/env python3
"""
Automatische Übersetzung der part_database.json
Konvertiert String-Format zu Multi-Language-Objekt-Format

Unterstützte Übersetzungs-APIs:
- DeepL (empfohlen für Qualität)
- Google Translate (kostenlos via googletrans)
- OpenAI (sehr gut, aber kostenpflichtig)
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List

# ===== Konfiguration =====
SOURCE_LANGUAGE = 'de'  # Quellsprache in der JSON
TARGET_LANGUAGES = ['en', 'fr']  # Sprachen zum Übersetzen

# DeepL API Einstellungen (optional)
DEEPL_API_KEY = None  # Hier deinen DeepL API Key einfügen

# OpenAI API Einstellungen (optional) 
OPENAI_API_KEY = None  # Hier deinen OpenAI API Key einfügen


class Translator:
    """Basis-Klasse für Übersetzer"""
    
    def translate(self, text: str, source: str, target: str) -> str:
        raise NotImplementedError


class DeepLTranslator(Translator):
    """DeepL Translator - Beste Qualität für europäische Sprachen"""
    
    def __init__(self, api_key: str):
        try:
            import deepl
            self.translator = deepl.Translator(api_key)
        except ImportError:
            raise ImportError("DeepL library nicht installiert. Führe aus: pip install deepl")
    
    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip():
            return text
        
        # DeepL erwartet 'EN-US' oder 'EN-GB', wir vereinfachen auf 'EN'
        target_lang = target.upper()
        if target_lang == 'EN':
            target_lang = 'EN-US'
        
        result = self.translator.translate_text(text, source_lang=source.upper(), target_lang=target_lang)
        return result.text


class GoogleTranslator(Translator):
    """Google Translate - Kostenlos via googletrans library"""
    
    def __init__(self):
        try:
            from googletrans import Translator as GT
            self.translator = GT()
        except ImportError:
            raise ImportError("googletrans nicht installiert. Führe aus: pip install googletrans==4.0.0-rc1")
    
    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip():
            return text
        
        result = self.translator.translate(text, src=source, dest=target)
        return result.text


class OpenAITranslator(Translator):
    """OpenAI GPT Translator - Sehr gute Qualität"""
    
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library nicht installiert. Führe aus: pip install openai")
    
    def translate(self, text: str, source: str, target: str) -> str:
        if not text.strip():
            return text
        
        language_names = {
            'de': 'German',
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
        }
        
        prompt = f"Translate the following {language_names.get(source, source)} text to {language_names.get(target, target)}. Only return the translation, nothing else:\n\n{text}"
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()


class DatabaseTranslator:
    """Hauptklasse für die Datenbank-Übersetzung"""
    
    def __init__(self, translator: Translator, source_lang: str, target_langs: List[str]):
        self.translator = translator
        self.source_lang = source_lang
        self.target_langs = target_langs
        self.stats = {
            'total_parts': 0,
            'translated_parts': 0,
            'skipped_parts': 0,
            'errors': 0,
        }
    
    def convert_to_multilang_format(self, data: Dict) -> Dict:
        """Konvertiert JSON von String-Format zu Multi-Language-Format"""
        result = {}
        total_parts = len(data)
        
        print(f"\n🌍 Starte Übersetzung von {total_parts} Teilen...")
        print(f"Quellsprache: {self.source_lang}")
        print(f"Zielsprachen: {', '.join(self.target_langs)}\n")
        
        for idx, (part_id, part_data) in enumerate(data.items(), 1):
            print(f"[{idx}/{total_parts}] Teil {part_id}...", end=' ')
            
            try:
                # Kopiere Basis-Daten
                result[part_id] = {
                    'category': part_data.get('category', ''),
                    'technicalDetails': part_data.get('technicalDetails', {}),
                    'imagePath': part_data.get('imagePath', ''),
                }
                
                # Verarbeite name
                name_value = part_data.get('name', '')
                if isinstance(name_value, str):
                    # String-Format -> konvertiere zu Multi-Language
                    name_translations = {self.source_lang: name_value}
                    
                    for target_lang in self.target_langs:
                        translated = self.translator.translate(name_value, self.source_lang, target_lang)
                        name_translations[target_lang] = translated
                    
                    result[part_id]['name'] = name_translations
                else:
                    # Bereits Multi-Language Format
                    result[part_id]['name'] = name_value
                
                # Verarbeite description
                desc_value = part_data.get('description', '')
                if isinstance(desc_value, str):
                    # String-Format -> konvertiere zu Multi-Language
                    desc_translations = {self.source_lang: desc_value}
                    
                    for target_lang in self.target_langs:
                        translated = self.translator.translate(desc_value, self.source_lang, target_lang)
                        desc_translations[target_lang] = translated
                    
                    result[part_id]['description'] = desc_translations
                else:
                    # Bereits Multi-Language Format
                    result[part_id]['description'] = desc_value
                
                print("✅")
                self.stats['translated_parts'] += 1
                
            except Exception as e:
                print(f"❌ Fehler: {e}")
                # Bei Fehler: Original-Daten behalten
                result[part_id] = part_data
                self.stats['errors'] += 1
        
        self.stats['total_parts'] = total_parts
        return result
    
    def print_stats(self):
        """Gibt Statistiken aus"""
        print("\n" + "="*50)
        print("📊 Übersetzungs-Statistik")
        print("="*50)
        print(f"Gesamt Teile:       {self.stats['total_parts']}")
        print(f"Erfolgreich:        {self.stats['translated_parts']} ✅")
        print(f"Fehler:             {self.stats['errors']} ❌")
        print("="*50)


def main():
    parser = argparse.ArgumentParser(description='Übersetze part_database.json')
    parser.add_argument('--input', '-i', default='part_database.json', 
                       help='Eingabe JSON Datei')
    parser.add_argument('--output', '-o', default='part_database_multilang.json',
                       help='Ausgabe JSON Datei')
    parser.add_argument('--translator', '-t', choices=['deepl', 'google', 'openai'],
                       default='google', help='Übersetzungs-Service')
    parser.add_argument('--languages', '-l', nargs='+', default=['en'],
                       help='Ziel-Sprachen (z.B. en fr es)')
    parser.add_argument('--backup', '-b', action='store_true',
                       help='Erstelle Backup der Original-Datei')
    
    args = parser.parse_args()
    
    # Lade JSON
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fehler: Datei {input_path} nicht gefunden!")
        return
    
    print(f"📂 Lade {input_path}...")
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Backup erstellen
    if args.backup:
        backup_path = input_path.with_suffix('.json.backup')
        print(f"💾 Erstelle Backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Wähle Übersetzer
    print(f"\n🔧 Initialisiere {args.translator.upper()} Übersetzer...")
    
    if args.translator == 'deepl':
        if not DEEPL_API_KEY:
            print("❌ Fehler: DEEPL_API_KEY nicht gesetzt!")
            print("Setze DEEPL_API_KEY im Script oder als Umgebungsvariable")
            return
        translator = DeepLTranslator(DEEPL_API_KEY)
    
    elif args.translator == 'google':
        translator = GoogleTranslator()
    
    elif args.translator == 'openai':
        if not OPENAI_API_KEY:
            print("❌ Fehler: OPENAI_API_KEY nicht gesetzt!")
            print("Setze OPENAI_API_KEY im Script oder als Umgebungsvariable")
            return
        translator = OpenAITranslator(OPENAI_API_KEY)
    
    # Übersetze
    db_translator = DatabaseTranslator(translator, SOURCE_LANGUAGE, args.languages)
    translated_data = db_translator.convert_to_multilang_format(data)
    
    # Speichere Ergebnis
    output_path = Path(args.output)
    print(f"\n💾 Speichere Ergebnis in {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    # Zeige Statistik
    db_translator.print_stats()
    
    print(f"\n✨ Fertig! Übersetzte Datei: {output_path}")
    print(f"\n⚠️  WICHTIG: Prüfe die Übersetzungen manuell!")
    print(f"⚠️  Erhöhe danach die Datenbankversion in database_version_manager.dart")


if __name__ == '__main__':
    main()
