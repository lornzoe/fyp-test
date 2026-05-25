#!/usr/bin/env python3
import os
from datetime import datetime

# Suppress annoying TensorFlow warning logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns

from mediapipe_model_maker import gesture_recognizer

def main():
    # ---------------------------------------------------------
    # 1. Configuration & Paths
    # ---------------------------------------------------------
    assert tf.__version__.startswith('2'), "TensorFlow 2.x is required."
    
    # This must match the TARGET_BASE_DIR from your subsample/stratify script
    STRATIFIED_ROOT = "HaGRIDv2_dataset_stratified" 
    EXPORT_DIR = f"exported_model_{datetime.now():%Y%m%d_%H%M%S}"
    
    os.makedirs(EXPORT_DIR, exist_ok=True)
    print(f"Using export directory: {EXPORT_DIR}")

    # Quick validation check to prevent running if paths are wrong
    train_root_check = os.path.join(STRATIFIED_ROOT, "train")
    if not os.path.exists(train_root_check):
        print(f"ERROR: Cannot find '{train_root_check}'. Did you run the stratification script first?")
        return

    # ---------------------------------------------------------
    # 2. Load Pre-Stratified Data Direct from Folders
    # ---------------------------------------------------------
    preprocessing_params = gesture_recognizer.HandDataPreprocessingParams()

    print("\nLoading pre-stratified Training pool...")
    train_data = gesture_recognizer.Dataset.from_folder(
        dirname=os.path.join(STRATIFIED_ROOT, "train"),
        hparams=preprocessing_params
    )

    print("Loading pre-stratified Validation pool...")
    validation_data = gesture_recognizer.Dataset.from_folder(
        dirname=os.path.join(STRATIFIED_ROOT, "validation"),
        hparams=preprocessing_params
    )

    print("Loading pre-stratified Test pool...")
    test_data = gesture_recognizer.Dataset.from_folder(
        dirname=os.path.join(STRATIFIED_ROOT, "test"),
        hparams=preprocessing_params
    )

    print(f"\n[Dataset Stratification Verification]")
    print(f"Train Dataset Size: {len(train_data)}  (Expected: ~50,176)")
    print(f"Val Dataset Size:   {len(validation_data)}  (Expected: ~3,584)")
    print(f"Test Dataset Size:  {len(test_data)}  (Expected: ~3,584)\n")

    # ---------------------------------------------------------
    # 3. Model Training
    # ---------------------------------------------------------
    hparams = gesture_recognizer.HParams(
        export_dir=EXPORT_DIR,
        epochs=40,
        learning_rate=0.001,
        batch_size=64,
        lr_decay=0.99
    )
    
    options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)

    print("Starting model training...")
    model = gesture_recognizer.GestureRecognizer.create(
        train_data=train_data,
        validation_data=validation_data,
        options=options
    )

    # ---------------------------------------------------------
    # 4. Base Evaluation
    # ---------------------------------------------------------
    print("\nEvaluating model against testing pool...")
    loss, acc = model.evaluate(test_data, batch_size=1)
    print(f"Test loss: {loss:.4f}, Test accuracy: {acc:.4f}\n")

    # ---------------------------------------------------------
    # 5. Detailed Metrics & Confusion Matrix
    # ---------------------------------------------------------
    print("Computing predictions on test data for Confusion Matrix...")
    
    # Extract the underlying Keras model and TensorFlow Dataset
    keras_model = model._model
    tf_test_dataset = test_data.gen_tf_dataset(batch_size=64)
    
    all_predictions = []
    all_labels = []
    
    # Iterate through the TensorFlow dataset batches
    for features, labels in tf_test_dataset:
        # Get Keras predictions for the batch
        preds = keras_model.predict_on_batch(features)
        batch_preds = np.argmax(preds, axis=1)
        all_predictions.extend(batch_preds)
        
        # Extract true labels (Safely handles both one-hot and integer arrays)
        if len(labels.shape) > 1 and labels.shape[1] > 1:
            batch_labels = np.argmax(labels.numpy(), axis=1)
        else:
            batch_labels = labels.numpy()
        all_labels.extend(batch_labels)

    # Map the integer IDs back to their actual string class names
    class_names = test_data.label_names
    all_predictions_strs = [class_names[i] for i in all_predictions]
    all_labels_strs = [class_names[i] for i in all_labels]

    classes = sorted(class_names)
    cm = confusion_matrix(all_labels_strs, all_predictions_strs, labels=classes)
    
    precision = precision_score(all_labels_strs, all_predictions_strs, average='weighted', zero_division=0)
    recall = recall_score(all_labels_strs, all_predictions_strs, average='weighted', zero_division=0)
    f1 = f1_score(all_labels_strs, all_predictions_strs, average='weighted', zero_division=0)

    print("\n--- Detailed Metrics ---")
    print(f"Precision: {precision:.4f} | Recall: {recall:.4f} | F1-Score: {f1:.4f}\n")
    print(classification_report(all_labels_strs, all_predictions_strs, labels=classes, zero_division=0))

    # Generate and save plot safely without GUI display requirements
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix - Gesture Recognition Test Set')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'{EXPORT_DIR}/confusion_matrix.png', dpi=100, bbox_inches='tight')
    print(f"Confusion matrix visualization saved to {EXPORT_DIR}/confusion_matrix.png")

    # ---------------------------------------------------------
    # 6. Export Model
    # ---------------------------------------------------------
    print("\nExporting compiled model asset bundle...")
    model.export_model()
    print(f"Model exported successfully to {EXPORT_DIR}/gesture_recognizer.task")

if __name__ == "__main__":
    main()