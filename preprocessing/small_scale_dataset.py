import os
import random
import numpy as np
from PIL import Image
from tqdm import tqdm

# --- CONFIG ---
# Corrected LOGO_DIR to point to the folder containing individual team directories
LOGO_DIR = 'footbal_team_logos/epl-logos-big/epl-logos-big'
BG_DIR = 'simple_images'
OUT_DIR = 'YOLO_SmallScale_Dataset'

TEAMS = sorted([d for d in os.listdir(LOGO_DIR) if os.path.isdir(os.path.join(LOGO_DIR, d))])
IMAGES_PER_TEAM = 500  # How many synthetic images to generate per team

def create_synthetic_data():
    # Create both train and val structures upfront
    for split in ["train", "val"]:
        os.makedirs(os.path.join(OUT_DIR, "images", split), exist_ok=True)
        os.makedirs(os.path.join(OUT_DIR, "labels", split), exist_ok=True)

    bg_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(BG_DIR) for f in filenames if f.endswith(('.jpg', '.png'))]

    for class_id, team in enumerate(TEAMS):
        print(f"Generating small-scale data for {team}...")
        team_path = os.path.join(LOGO_DIR, team)
        # Filter for actual image files within the team's directory
        team_logos = [os.path.join(team_path, f) for f in os.listdir(team_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not team_logos: # Added check for empty team_logos
            print(f"WARNING: No image files found for team '{team}' in '{team_path}'. Skipping generation for this team.")
            continue # Skip to the next team

        for i in tqdm(range(IMAGES_PER_TEAM)):
            # 1. Pick random background and logo
            bg = Image.open(random.choice(bg_files)).convert("RGB")
            logo = Image.open(random.choice(team_logos)).convert("RGBA")

            bg_w, bg_h = bg.size

            # 2. Randomly scale logo (between 3% and 12% of background width)
            scale_factor = random.uniform(0.03, 0.12)
            new_logo_w = int(bg_w * scale_factor)
            # Maintain aspect ratio
            w_percent = (new_logo_w / float(logo.size[0]))
            new_logo_h = int((float(logo.size[1]) * float(w_percent)))
            logo = logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)

            # 3. Pick random position (ensure it stays inside the frame)
            max_x = max(0, bg_w - new_logo_w)
            max_y = max(0, bg_h - new_logo_h)
            paste_x = random.randint(0, max_x)
            paste_y = random.randint(0, max_y)

            # 4. Paste logo onto background
            # We use the logo as the mask to handle transparency/rounded corners
            bg.paste(logo, (paste_x, paste_y), logo)

            # 5. Calculate YOLO Coordinates (Normalized 0 to 1)
            x_center = (paste_x + (new_logo_w / 2)) / bg_w
            y_center = (paste_y + (new_logo_h / 2)) / bg_h
            width = new_logo_w / bg_w
            height = new_logo_h / bg_h

            # 6. Save Image and Label
            img_name = f"synth_{team}_{i}.jpg"
            bg.save(os.path.join(OUT_DIR, "images", "train", img_name))

            with open(os.path.join(OUT_DIR, "labels", "train", f"synth_{team}_{i}.txt"), 'w') as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

create_synthetic_data()