import os
from skimage.io import imread, imsave
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2
from cellpose import models, io

# ==== CONFIGURATION ====
# Change these paths to match your system
jpg_folder = "/Users/luzguevara/Documents/proyecto_cellpose/data"
video_path = "/Users/luzguevara/Downloads/Hela_CM30.avi"
output_folder = "/Users/luzguevara/Documents/proyecto_cellpose/results"
os.makedirs(output_folder, exist_ok=True)

# Initialize Cellpose v4 model
print("Loading Cellpose model...")
model = models.CellposeModel(gpu=True)  # Use GPU if available
print("Model loaded.")

# ==== PROCESS JPG IMAGES ====
print("Processing JPG images...")
image_files = sorted([f for f in os.listdir(jpg_folder) if f.endswith('.jpg')])
jpg_data = []

for idx, file in enumerate(image_files):
    img_path = os.path.join(jpg_folder, file)
    image = imread(img_path)

    # Segmentation
    masks, flows, styles, diams = model.eval(image, cellprob_threshold=0.0, diameter=None)
    overlay = io.color_labels(masks)

    # Save mask
    mask_file = os.path.join(output_folder, f"mask_{idx:03}.png")
    imsave(mask_file, overlay)

    # Calculate metrics
    num_cells = np.unique(masks).size - 1
    areas = [np.sum(masks == i) for i in np.unique(masks) if i != 0]
    avg_area = np.mean(areas) if areas else 0
    avg_brightness = np.mean(image[masks > 0]) if np.any(masks > 0) else 0

    jpg_data.append([idx, num_cells, avg_area, avg_brightness])
    print(f"Processed {file}: {num_cells} cells")

# ==== SAVE JPG SUMMARY ====
jpg_df = pd.DataFrame(jpg_data, columns=["Frame", "NumCells", "AvgArea", "AvgBrightness"])
jpg_df.to_csv(os.path.join(output_folder, "jpg_summary.csv"), index=False)
print("Summary of JPG images saved.")

# ==== CREATE VIDEO WITH MASKS ====
print("Creating video with JPG masks...")
height, width, _ = overlay.shape
out_jpg = cv2.VideoWriter(os.path.join(output_folder, "jpg_masked_output.avi"),
                          cv2.VideoWriter_fourcc(*'XVID'), 10, (width, height))

for idx in range(len(image_files)):
    frame = imread(os.path.join(output_folder, f"mask_{idx:03}.png"))
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out_jpg.write(frame_bgr)
out_jpg.release()
print("Video of JPG masks created.")

# ==== PROCESS AVI VIDEO ====
print("Processing AVI video...")
cap = cv2.VideoCapture(video_path)
avi_data = []
frame_idx = 0

# Configure video output
out_avi = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Segmentation
    masks, flows, styles, diams = model.eval(gray, cellprob_threshold=0.0, diameter=None)
    overlay = io.color_labels(masks)
    combined = cv2.addWeighted(frame, 0.6, overlay, 0.4, 0)

    # Calculate metrics
    num_cells = np.unique(masks).size - 1
    areas = [np.sum(masks == i) for i in np.unique(masks) if i != 0]
    avg_area = np.mean(areas) if areas else 0
    avg_brightness = np.mean(gray[masks > 0]) if np.any(masks > 0) else 0

    avi_data.append([frame_idx, num_cells, avg_area, avg_brightness])

    # Write frame to output video
    if out_avi is None:
        height, width, _ = combined.shape
        out_avi = cv2.VideoWriter(os.path.join(output_folder, "avi_masked_output.avi"),
                                  cv2.VideoWriter_fourcc(*'XVID'), 20, (width, height))
    out_avi.write(combined)

    frame_idx += 1
    print(f"Processed frame {frame_idx}")

cap.release()
if out_avi:
    out_avi.release()
print("AVI video with masks created.")

# ==== SAVE AVI SUMMARY ====
avi_df = pd.DataFrame(avi_data, columns=["Frame", "NumCells", "AvgArea", "AvgBrightness"])
avi_df.to_csv(os.path.join(output_folder, "avi_summary.csv"), index=False)
print("Summary of AVI video saved.")

print("PROCESS COMPLETE")

