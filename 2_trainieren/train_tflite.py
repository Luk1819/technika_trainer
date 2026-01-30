import tensorflow as tf
import os

# 1. PARAMETER
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(script_dir, 'trainingsdaten')
OUTPUT_MODEL = os.path.join(script_dir, 'mein_modell.tflite')
OUTPUT_LABELS = os.path.join(script_dir, 'labels.txt')
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10 # Erhöhe auf 20-30 für bessere Genauigkeit

# Prüfen ob Trainingsdaten vorhanden sind
if not os.path.exists(DATA_DIR):
    print(f"FEHLER: Ordner '{DATA_DIR}' nicht gefunden!")
    print("Bitte kopiere den 'trainingsdaten' Ordner in diesen Ordner.")
    exit()

# 2. DATEN LADEN & AUFTEILEN
# Erstellt automatisch Labels basierend auf den Ordnernamen
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# 3. DATA AUGMENTATION (Macht das Modell robuster gegen Licht/Drehung)
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal_and_vertical"),
    tf.keras.layers.RandomRotation(0.2),
])

# 4. MODELL AUFBAUEN (MobileNetV2)
base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,), 
    include_top=False, 
    weights='imagenet'
)
base_model.trainable = False # Vorhandenes Wissen einfrieren

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=IMG_SIZE + (3,)),
    data_augmentation,
    tf.keras.layers.Rescaling(1./127.5, offset=-1), # MobileNet braucht Input von -1 bis 1
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(len(train_ds.class_names), activation='softmax')
])

# 5. KOMPILIEREN & TRAINIEREN
model.compile(optimizer='adam', 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

print("Starte Training...")
model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

# 6. EXPORT NACH TFLITE
print("Konvertiere zu TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Modell speichern
with open(OUTPUT_MODEL, 'wb') as f:
    f.write(tflite_model)

# Labels speichern (für die App)
with open(OUTPUT_LABELS, 'w', encoding='utf-8') as f:
    for class_name in train_ds.class_names:
        f.write(class_name + '\n')

print(f"Fertig! Dateien erstellt:")
print(f"  - Modell: {OUTPUT_MODEL}")
print(f"  - Labels: {OUTPUT_LABELS}")
print(f"  - Klassen: {', '.join(train_ds.class_names)}")