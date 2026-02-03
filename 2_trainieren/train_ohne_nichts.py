import tensorflow as tf
import os

# 1. PARAMETER
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(script_dir, 'trainingsdaten')
OUTPUT_MODEL = os.path.join(script_dir, 'modell_ohne_nichts.tflite')
OUTPUT_LABELS = os.path.join(script_dir, 'labels_ohne_nichts.txt')
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 30
FINE_TUNE_EPOCHS = 15

# 2. DATEN LADEN - NUR DIE TEILE (ohne "nichts")
# Erstelle Liste der Klassen ohne "nichts"
class_names_to_include = ['137096', '31021', '37783']

# Lade alle Daten
all_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False  # Wichtig für manuelles Filtern
)

print(f"Verfügbare Klassen: {all_ds.class_names}")

# Filtere nur die gewünschten Klassen
def filter_classes(image, label):
    # Behalte nur Labels 0, 1, 2 (entspricht 137096, 31021, 37783)
    return tf.reduce_any(tf.equal(label, [0, 1, 2]))

# Wende Filter an und remapped Labels
filtered_ds = all_ds.unbatch().filter(filter_classes).batch(BATCH_SIZE)

# Aufteilen in Training und Validation (80/20)
dataset_size = sum(1 for _ in filtered_ds.unbatch())
train_size = int(0.8 * dataset_size)

train_ds = filtered_ds.unbatch().take(train_size).batch(BATCH_SIZE)
val_ds = filtered_ds.unbatch().skip(train_size).batch(BATCH_SIZE)

print(f"Training Samples: ~{train_size}")
print(f"Validation Samples: ~{dataset_size - train_size}")

# 3. DATA AUGMENTATION
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomBrightness(0.2),
])

# 4. MODELL AUFBAUEN
base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,), 
    include_top=False, 
    weights='imagenet'
)
base_model.trainable = False

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=IMG_SIZE + (3,)),
    data_augmentation,
    tf.keras.layers.Rescaling(1./127.5, offset=-1),
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(3, activation='softmax')  # Nur 3 Klassen!
])

# 5. KOMPILIEREN & TRAINIEREN
model.compile(optimizer='adam', 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

print("\nStarte Training OHNE 'nichts' Klasse (Phase 1)...")
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

# PHASE 2: FINE-TUNING
print("\nStarte Fine-Tuning (Phase 2)...")
base_model.trainable = True
for layer in base_model.layers[:100]:
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history_fine = model.fit(train_ds, validation_data=val_ds, epochs=FINE_TUNE_EPOCHS)

# 6. EXPORT NACH TFLITE
print("\nKonvertiere zu TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open(OUTPUT_MODEL, 'wb') as f:
    f.write(tflite_model)

# Labels speichern (nur die 3 Teile)
with open(OUTPUT_LABELS, 'w', encoding='utf-8') as f:
    for class_name in class_names_to_include:
        f.write(class_name + '\n')

print(f"\nFertig! Dateien erstellt:")
print(f"  - Modell: {OUTPUT_MODEL}")
print(f"  - Labels: {OUTPUT_LABELS}")
print(f"  - Klassen: {', '.join(class_names_to_include)}")
