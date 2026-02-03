import cv2
import numpy as np
import tensorflow as tf
import os

# Pfade basierend auf Script-Ordner
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "mein_modell.tflite")
labels_path = os.path.join(script_dir, "labels.txt")

# Überprüfung ob Dateien vorhanden sind
if not os.path.exists(model_path):
    print(f"FEHLER: Modell nicht gefunden: {model_path}")
    print("Bitte kopiere 'mein_modell.tflite' in diesen Ordner.")
    exit()

if not os.path.exists(labels_path):
    print(f"FEHLER: Labels nicht gefunden: {labels_path}")
    print("Bitte kopiere 'labels.txt' in diesen Ordner.")
    exit()

# 1. MODELL LADEN
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Details über Input und Output abfragen
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Labels aus Datei laden
with open(labels_path, 'r', encoding='utf-8') as f:
    classes = [line.strip() for line in f.readlines()]

print(f"Modell geladen: {len(classes)} Klassen erkannt")
print(f"Klassen: {', '.join(classes)}")
print() 

cap = cv2.VideoCapture(1)

print("Starte Live-Erkennung... Drücke 'Q' zum Beenden.")

while True:
    ret, frame = cap.read()
    if not ret: break

    # 2. BILD VORBEREITEN (Preprocessing)
    # Genau wie im Training: Größe ändern und Normalisierung
    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # WICHTIG: OpenCV nutzt BGR, TensorFlow RGB!
    img = img.astype(np.float32)
    img = (img / 127.5) - 1.0  # MobileNetV2 Skalierung: von [0,255] zu [-1,1]
    img = np.expand_dims(img, axis=0) # Batch-Dimension hinzufügen

    # 3. INFERENZ (Vorhersage)
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    # Ergebnis auswerten
    prediction_idx = np.argmax(output_data[0])
    confidence = output_data[0][prediction_idx]
    label = classes[prediction_idx]

    # 4. ANZEIGE
    color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255) # Grün wenn sicher
    text = f"{label} ({confidence*100:.1f}%)"
    
    cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    # Zeige alle Wahrscheinlichkeiten für Debugging
    y_offset = 100
    for i, class_name in enumerate(classes):
        prob_text = f"{class_name}: {output_data[0][i]*100:.1f}%"
        cv2.putText(frame, prob_text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 30
    
    cv2.imshow('TFLite Live Test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()