import os
import shutil
import random

# --- CONFIGURATION ---
SOURCE_LOGOS = 'footbal_team_logos/epl-logos-big/epl-logos-big'
SOURCE_NOISE = 'simple_images'
DEST_ROOT = 'YOLO_Dataset'

LOGOS_LIMIT = 500
DESIRED_NOISE_COUNT = 800  # We will oversample to reach this

def process_final_dataset():
    # Create structure
    for p in [f'{DEST_ROOT}/images/train', f'{DEST_ROOT}/labels/train']:
        if os.path.exists(p): shutil.rmtree(p)
        os.makedirs(p)

    teams = sorted([d for d in os.listdir(SOURCE_LOGOS) if os.path.isdir(os.path.join(SOURCE_LOGOS, d))])
    
    # 1. Process 500 Logos per Team
    print(f"Moving 500 logos for {len(teams)} teams...")
    for class_id, team_name in enumerate(teams):
        team_dir = os.path.join(SOURCE_LOGOS, team_name)
        images = sorted([f for f in os.listdir(team_dir)])[:LOGOS_LIMIT]
        
        for img_file in images:
            new_name = f"{team_name}_{img_file}"
            shutil.copy(os.path.join(team_dir, img_file), os.path.join(DEST_ROOT, 'images/train', new_name))
            
            # Label for logo
            label_name = os.path.splitext(new_name)[0] + ".txt"
            with open(os.path.join(DEST_ROOT, 'labels/train', label_name), 'w') as f:
                f.write(f"{class_id} 0.5 0.5 0.8 0.8\n")

    # 2. Oversample Noise to reach 800
    noise_pool = []
    for root, _, files in os.walk(SOURCE_NOISE):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                noise_pool.append(os.path.join(root, f))

    print(f"Found {len(noise_pool)} unique noise images. Sampling to reach {DESIRED_NOISE_COUNT}...")
    
    # random.choices allows duplicates (oversampling)
    selected_noise = random.choices(noise_pool, k=DESIRED_NOISE_COUNT)

    for i, noise_path in enumerate(selected_noise):
        ext = os.path.splitext(noise_path)[1]
        # We give each a unique name (e.g., bg_0, bg_1...) so the OS allows the copy
        new_bg_name = f"bg_{i}{ext}" 
        
        shutil.copy(noise_path, os.path.join(DEST_ROOT, 'images/train', new_bg_name))
        
        # Empty label for background
        label_name = os.path.splitext(new_bg_name)[0] + ".txt"
        open(os.path.join(DEST_ROOT, 'labels/train', label_name), 'w').close()

    print(f"\nDone! Dataset ready with {len(teams)*LOGOS_LIMIT} logos and {DESIRED_NOISE_COUNT} noise images.")

if __name__ == "__main__":
    process_final_dataset()