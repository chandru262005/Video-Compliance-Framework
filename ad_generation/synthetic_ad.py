#inserts logo at random location and timestamp

import cv2
import os
import random
import numpy as np

# --- CONFIG ---
VIDEO_PATH = 'videoplayback.mp4'
LOGO_DIR = 'footbal_team_logos/epl-logos-big/epl-logos-big'
OUTPUT_PATH = 'compliance_test.mp4'
MAX_SECONDS = 30 
GLITCH_DURATION = 0.75 # How long the logo stays on screen (in seconds)

def apply_overlay(img, logo, x, y):
    """Helper to overlay logo with transparency"""
    h, w = logo.shape[:2]
    # Ensure coordinates don't go out of frame
    y2, x2 = min(y+h, img.shape[0]), min(x+w, img.shape[1])
    h, w = y2-y, x2-x
    
    overlay = logo[:h, :w, :3]
    mask = logo[:h, :w, :3] / 255.0 # Use RGB values as mask if alpha is missing, or logo[:,:,3]
    if logo.shape[2] == 4:
        mask = logo[:h, :w, 3] / 255.0
        for c in range(0, 3):
            img[y:y2, x:x2, c] = (overlay[:, :, c] * mask) + (img[y:y2, x:x2, c] * (1.0 - mask))
    return img

def create_glitch_video():
    cap = cv2.VideoCapture(VIDEO_PATH)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    
    out = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # 1. Setup Timestamps (Random moments within 30s)
    # Event 1 starts between 2s and 10s | Event 2 starts between 15s and 25s
    start_time1 = random.uniform(2.0, 10.0)
    start_time2 = random.uniform(15.0, 25.0)
    
    # Convert seconds to frame numbers
    frames_glitch = int(GLITCH_DURATION * fps)
    range1 = (int(start_time1 * fps), int(start_time1 * fps) + frames_glitch)
    range2 = (int(start_time2 * fps), int(start_time2 * fps) + frames_glitch)

    # 2. Pick Logos and Random Positions
    all_teams = [d for d in os.listdir(LOGO_DIR) if os.path.isdir(os.path.join(LOGO_DIR, d))]
    team1, team2 = random.sample(all_teams, 2)
    
    l1 = cv2.imread(os.path.join(LOGO_DIR, team1, random.choice(os.listdir(os.path.join(LOGO_DIR, team1)))), cv2.IMREAD_UNCHANGED)
    l2 = cv2.imread(os.path.join(LOGO_DIR, team2, random.choice(os.listdir(os.path.join(LOGO_DIR, team2)))), cv2.IMREAD_UNCHANGED)
    
    size = int(height * 0.15)
    l1 = cv2.resize(l1, (size, size))
    l2 = cv2.resize(l2, (size, size))

    pos1 = (random.randint(50, width-size-50), random.randint(50, height-size-50))
    pos2 = (random.randint(50, width-size-50), random.randint(50, height-size-50))

    print(f"🚀 Glitch 1: {team1} at {start_time1:.2f}s")
    print(f"🚀 Glitch 2: {team2} at {start_time2:.2f}s")

    frame_idx = 0
    while cap.isOpened() and frame_idx < (MAX_SECONDS * fps):
        ret, frame = cap.read()
        if not ret: break

        # Only draw if within the specific frame ranges
        if range1[0] <= frame_idx <= range1[1]:
            frame = apply_overlay(frame, l1, pos1[0], pos1[1])
        
        if range2[0] <= frame_idx <= range2[1]:
            frame = apply_overlay(frame, l2, pos2[0], pos2[1])

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print("✅ Glitch test video generated!")

create_glitch_video()