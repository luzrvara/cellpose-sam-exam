# 🧬 Cellpose SAM Pipeline – Cell Segmentation & Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python) ![License](https://img.shields.io/badge/license-MIT-green) ![Status](https://img.shields.io/badge/status-active-brightgreen)

This repository contains a Python pipeline that uses **Cellpose v4 (SAM)** to process image sequences and videos for **cell segmentation, classification, and quantitative analysis**.

[![🔗 View Results on Google Drive](https://img.shields.io/badge/🔗%20View%20Results-Google%20Drive-blue?logo=google-drive)](https://drive.google.com/drive/folders/1i8w17uhnUv0pBY_HZ32-bCUXai5-dcO-?usp=share_link)

---

## 🚀 Features

✅ Segment cells in `.jpg` image sequences and `.avi` videos  
✅ Automatically compute **frame-by-frame metrics**:  
- Total cell count  
- Average area of detected cells  
- Average brightness of cells  
✅ Generate **colored mask overlays** and **output videos**  
✅ Export **CSV summaries** with quantitative data

---

## 🗺️ Pipeline Workflow

```mermaid
flowchart LR
A[Input JPG Images / AVI Video] --> B[Cellpose v4 SAM Segmentation]
B --> C[Mask Generation & Overlay]
C --> D[Metric Calculation (Count, Area, Brightness)]
C --> E[Output Videos with Masks]
D --> F[Export CSV Summary]
E --> F
```
## 🖼️ Example Output

### 🎥 Masked Video Frame
<p align="center">
  <img src="results/example_frame.png" width="600" alt="Masked frame example">
</p>

✅ Cells are segmented and overlaid with color-coded masks:  

| Class Name             | Description                      | Color    |
|------------------------|------------------------------------|----------|
| **Circular_viva**      | Live circular cells (initial frames) | 🟢 Green |
| **Fija**               | Fixed cells (middle frames)         | 🟡 Yellow|
| **Circular_muerta**    | Dead circular cells (late frames)   | 🔴 Red   |
| **Fragmento**          | Small fragments or debris           | 🟣 Magenta|

---

## ⚙️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/luzrvara/cellpose-sam-exam.git
   cd cellpose-sam-exam
```
2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv cellpose_env
source cellpose_env/bin/activate  # On macOS/Linux
cellpose_env\Scripts\activate     # On Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
## 📝 Usage

1️⃣ Place your input `.jpg` images in the `data/` folder  
2️⃣ Update paths for input/output folders in `cellpose_exam_pipeline.py` (lines 8–11)  
3️⃣ Run the script:

```bash
python cellpose_exam_pipeline.py
```
4️⃣ Check the results/ folder for output videos and CSV summaries

## 📊 Example Results

🎥 Videos:

- `jpg_masked_output.avi`: Masked video from `.jpg` images  
- `avi_masked_output.avi`: Masked video from input `.avi` file

📈 CSV Output Example:

| Frame | NumCells | AvgArea | AvgBrightness |
|-------|----------|---------|---------------|
| 0     | 152      | 320.4   | 128.5         |
| 1     | 148      | 315.2   | 130.1         |

---

## 👩🏻‍💻 Author

**Luz Guevara**  
📧 gluzrvara@gmail.com  
🌐 [GitHub Profile](https://github.com/luzrvara)
