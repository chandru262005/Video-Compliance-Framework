import os
import random
import shutil
from tqdm import tqdm

# --- CONFIG ---
DATASET_ROOT = 'YOLO_SmallScale_Dataset'
VAL_RATIO = 0.2  # 20% for validation

def split_dataset():
    train_images_dir = os.path.join(DATASET_ROOT, 'images', 'train')
    train_labels_dir = os.path.join(DATASET_ROOT, 'labels', 'train')
    
    val_images_dir = os.path.join(DATASET_ROOT, 'images', 'val')
    val_labels_dir = os.path.join(DATASET_ROOT, 'labels', 'val')

    # Ensure validation directories exist
    os.makedirs(val_images_dir, exist_ok=True)
    os.makedirs(val_labels_dir, exist_ok=True)

    # Get all image files in train
    images = [f for f in os.listdir(train_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        print("No images found in the train folder.")
        return

    # Randomly shuffle and pick validation set
    num_val = int(len(images) * VAL_RATIO)
    val_subset = random.sample(images, num_val)

    print(f"Moving {num_val} files from train to val (Ratio: {VAL_RATIO})...")

    for img_file in tqdm(val_subset):
        # Image path
        src_img = os.path.join(train_images_dir, img_file)
        dst_img = os.path.join(val_images_dir, img_file)
        
        # Label path (assuming same name but .txt)
        label_file = os.path.splitext(img_file)[0] + '.txt'
        src_label = os.path.join(train_labels_dir, label_file)
        dst_label = os.path.join(val_labels_dir, label_file)

        # Move image
        if os.path.exists(src_img):
            shutil.move(src_img, dst_img)
        
        # Move label if it exists
        if os.path.exists(src_label):
            shutil.move(src_label, dst_label)

    print(f"Done! Dataset split complete.")
    print(f"Train: {len(os.listdir(train_images_dir))} images")
    print(f"Val: {len(os.listdir(val_images_dir))} images")

if __name__ == "__main__":
    split_dataset()
