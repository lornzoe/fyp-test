#!/usr/bin/env python3
import os
import random
import shutil

# ==========================================
# CONFIGURATION
# ==========================================
SOURCE_DIR = "HaGRIDv2_dataset_512"
TARGET_BASE_DIR = "HaGRIDv2_dataset_stratified"

# Maximum targeted images per class for TRAINING & VALIDATION limits
TOTAL_PER_CLASS = 2048

# Upper limit cap for the test dataset split per class
MAX_TEST_PER_CLASS = 2048

# Ratios for splitting the training/validation limits
TRAIN_RATIO = 0.875  
VAL_RATIO = 0.0625   

USE_SYMLINKS = True

# Set deterministic seed for reproducible splits
random.seed(42)

# ==========================================
# EXECUTION LOGIC
# ==========================================
def main():
    if os.path.exists(TARGET_BASE_DIR):
        print(f"Clearing old target tree: {TARGET_BASE_DIR}")
        shutil.rmtree(TARGET_BASE_DIR)

    classes = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d)) and not d.startswith('.')]

    print(f"Found {len(classes)} classes. Beginning Exhaustive Test Stratification (Max Test Cap: {MAX_TEST_PER_CLASS})...")
    print("-" * 85)

    for class_name in classes:
        source_class_dir = os.path.join(SOURCE_DIR, class_name)
        files = [f for f in os.listdir(source_class_dir) if os.path.isfile(os.path.join(source_class_dir, f)) and not f.startswith('.')]
        
        # Shuffle the files first deterministically using our random seed
        random.shuffle(files)
        pool_size = len(files)

        if pool_size < TOTAL_PER_CLASS:
            print(f"Note: Class '{class_name}' only has {pool_size} files (Cap is {TOTAL_PER_CLASS}).")
            # Proportional fallback splits if data is shorter than cap limit
            train_count = int(pool_size * TRAIN_RATIO)
            val_count = int(pool_size * VAL_RATIO)
            
            train_pool = files[:train_count]
            val_pool = files[train_count : train_count + val_count]
            
            raw_test_pool = files[train_count + val_count:]
            # Apply maximum upper limit constraint to test subset
            test_count = min(MAX_TEST_PER_CLASS, len(raw_test_pool))
            test_pool = raw_test_pool[:test_count]
        else:
            # Calculate standard training and validation slices based on the cap limit
            train_count = int(TOTAL_PER_CLASS * TRAIN_RATIO)
            val_count = int(TOTAL_PER_CLASS * VAL_RATIO)
            
            # Carve out training and validation from the very front of the shuffled list
            train_pool = files[:train_count]
            val_pool = files[train_count : train_count + val_count]
            
            # Extract everything left behind for the potential exhaustive testing slice
            raw_test_pool = files[train_count + val_count:]
            
            # Apply maximum upper limit constraint to test subset
            test_count = min(MAX_TEST_PER_CLASS, len(raw_test_pool))
            test_pool = raw_test_pool[:test_count]

        # Map splits to folder structure
        splits = {
            "train": train_pool,
            "validation": val_pool,
            "test": test_pool
        }

        # Handle class name conversion for background requirements
        mapped_class_name = "none" if class_name == "no_gesture" else class_name

        for split_name, file_list in splits.items():
            target_folder = os.path.join(TARGET_BASE_DIR, split_name, mapped_class_name)
            os.makedirs(target_folder, exist_ok=True)
            
            for filename in file_list:
                src_path = os.path.abspath(os.path.join(source_class_dir, filename))
                dst_path = os.path.abspath(os.path.join(target_folder, filename))
                
                if USE_SYMLINKS:
                    try:
                        os.symlink(src_path, dst_path)
                    except OSError as e:
                        print(f"Error linking {filename}: {e}")
                else:
                    shutil.copy2(src_path, dst_path)
                    
        print(f"Class '{class_name}' -> '{mapped_class_name}' split complete.")
        print(f"Split distribution: Train: {len(train_pool)} | Val: {len(val_pool)} | Test Pool (Capped): {len(test_pool)}")
        print("-" * 85)

    print(f"\nExhaustive stratification tree written successfully to: ./{TARGET_BASE_DIR}")

if __name__ == "__main__":
    main()