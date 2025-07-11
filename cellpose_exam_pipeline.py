import os
import glob
import numpy as np
from skimage.io import imread
from skimage.measure import regionprops, label
import cv2
from tqdm import tqdm
import pandas as pd

from cellpose import models

# ======= CONFIGURACIÓN =======
DATA_DIR = "/Users/luzguevara/Documents/proyecto_cellpose/data/"
OUTPUT_DIR = "/Users/luzguevara/Documents/proyecto_cellpose/output/"
DIAMETER = 30  # Ajusta según tamaño celular en pixeles

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colores BGR para las 4 clases
CATEGORY_COLORS = {
    "Circular_viva": (0, 255, 0),      # Verde
    "Fija": (255, 255, 0),             # Amarillo
    "Circular_muerta": (0, 0, 255),    # Rojo
    "Fragmento": (255, 0, 255)         # Magenta
}

# ======= INICIALIZAR CELLPOSE =======
model = models.CellposeModel(gpu=True)

# ======= FUNCIONES =======
def clasificar_objeto(prop, stage):
    """Clasifica células según área, circularidad, brillo y etapa temporal"""
    area = prop.area
    perimeter = prop.perimeter if prop.perimeter > 0 else 1
    circularity = (4 * np.pi * area) / (perimeter ** 2)
    mean_intensity = prop.mean_intensity

    # Fragmentos por área pequeña
    if area < 50:
        return "Fragmento"

    if stage == "inicio":
        return "Circular_viva"
    elif stage == "medio":
        return "Fija"
    else:
        if circularity > 0.8 and mean_intensity < 100:
            return "Circular_muerta"
        else:
            return "Fija"

# ======= PROCESAR IMÁGENES =======
frame_paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.jpg")))
n_frames = len(frame_paths)
print(f"Encontrados {n_frames} frames.")

# Dividir etapas temporales
stage_boundaries = [int(n_frames * 0.33), int(n_frames * 0.66)]
stages = []
for i in range(n_frames):
    if i <= stage_boundaries[0]:
        stages.append("inicio")
    elif i <= stage_boundaries[1]:
        stages.append("medio")
    else:
        stages.append("final")

# Leer tamaño imagen para videos
sample_img = imread(frame_paths[0])
height, width = sample_img.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*"XVID")
fps = 10

# Videos: máscaras coloreadas, overlay, y uno por clase
video_masks = cv2.VideoWriter(os.path.join(OUTPUT_DIR, "masks_colored.avi"), fourcc, fps, (width, height))
video_overlay = cv2.VideoWriter(os.path.join(OUTPUT_DIR, "overlay.avi"), fourcc, fps, (width, height))

video_by_class = {}
for cat in CATEGORY_COLORS.keys():
    video_by_class[cat] = cv2.VideoWriter(os.path.join(OUTPUT_DIR, f"{cat}.avi"), fourcc, fps, (width, height))

# Resumen resultados
summary = []

for idx, (frame_path, stage) in enumerate(tqdm(zip(frame_paths, stages), total=n_frames, desc="Procesando frames")):
    img = imread(frame_path)

    # Segmentar con Cellpose
    result = model.eval(img, diameter=DIAMETER, cellprob_threshold=-0.8, flow_threshold=0.4, channels=[0, 0])
    masks = result[0]
    label_img = label(masks)
    props = regionprops(label_img, intensity_image=img)

    # Crear imágenes para videos
    overlay = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    mask_colored = np.zeros((height, width, 3), dtype=np.uint8)
    mask_classes = {cat: np.zeros((height, width, 3), dtype=np.uint8) for cat in CATEGORY_COLORS.keys()}

    # Contadores y métricas por clase
    frame_summary = {"Frame": os.path.basename(frame_path)}

    for cat in CATEGORY_COLORS.keys():
        frame_summary[f"{cat}_count"] = 0
        frame_summary[f"{cat}_avg_area"] = 0
        frame_summary[f"{cat}_avg_brightness"] = 0

    # Clasificar objetos
    for prop in props:
        cat = clasificar_objeto(prop, stage)
        coords = prop.coords
        color = CATEGORY_COLORS[cat]

        # Pintar en máscara general
        mask_colored[coords[:,0], coords[:,1], :] = color

        # Pintar en máscara específica
        mask_classes[cat][coords[:,0], coords[:,1], :] = color

        # Pintar en overlay
        overlay[coords[:,0], coords[:,1], :] = color

        # Actualizar métricas
        frame_summary[f"{cat}_count"] += 1
        frame_summary[f"{cat}_avg_area"] += prop.area
        frame_summary[f"{cat}_avg_brightness"] += prop.mean_intensity

    # Promediar métricas (evitar división por cero)
    for cat in CATEGORY_COLORS.keys():
        count = frame_summary[f"{cat}_count"]
        if count > 0:
            frame_summary[f"{cat}_avg_area"] /= count
            frame_summary[f"{cat}_avg_brightness"] /= count

    summary.append(frame_summary)

    # Escribir frames en videos
    video_masks.write(mask_colored)
    video_overlay.write(overlay)
    for cat, vid in video_by_class.items():
        vid.write(mask_classes[cat])

# Cerrar videos
video_masks.release()
video_overlay.release()
for vid in video_by_class.values():
    vid.release()

# Guardar CSV resumen
df = pd.DataFrame(summary)
csv_path = os.path.join(OUTPUT_DIR, "mediciones_por_frame.csv")
df.to_csv(csv_path, index=False)

print(f"\nProceso completado.")
print(f"Resultados CSV guardados en: {csv_path}")
print(f"Videos guardados en: {OUTPUT_DIR}")

