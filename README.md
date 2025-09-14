# 🖼️ AI Image Generator & Editor

An interactive **Streamlit web app** for generating, editing, and transforming images using Google **Gemini** models.  
Supports **Text → Image generation**, **Image Editing**, **Pose Transfer**, and keeps a **History** of all generated results.  

---

## 🚀 Features
- **Text → Image**  
  Generate high-quality images from text prompts. Optionally auto-enhance prompts for better results.  

- **Simple Edit**  
  Upload an image and describe edits (e.g., *“make the sky dramatic with orange and purple clouds”*).  

- **Pose Transfer**  
  Upload a **base image** and a **reference pose image** – the app extracts the pose and applies it to the base subject.  

- **History**  
  Browse, download, and reuse previously generated images.  

- **Prompt Enhancement (Optional)**  
  Automatically improves prompts for more vivid outputs.  

---

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) – Web UI  
- [Google Gemini API](https://ai.google.dev/) – Image & text models  
- [Pillow (PIL)](https://pillow.readthedocs.io/) – Image handling  
- Python standard libraries: `io`, `datetime`  

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-image-editor.git
   cd ai-image-editor
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # on macOS/Linux
   venv\Scripts\activate      # on Windows

   pip install -r requirements.txt
   ```

   Example `requirements.txt`:
   ```txt
   streamlit
   pillow
   google-genai
   ```

3. **Set up API Key**
   - Get your [Google API key](https://ai.google.dev/).  
   - Add it to `.streamlit/secrets.toml` (recommended) or enter it in the sidebar.  

   Example `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   ```

---

## ▶️ Usage

Run the app locally:
```bash
streamlit run app.py
```

Open the browser at [http://localhost:8501](http://localhost:8501).

---

## 📸 Screenshots

### 🔹 Text → Image
Generate new artwork with a single prompt.  

### 🔹 Simple Edit
Upload an image and describe transformations.  

### 🔹 Pose Transfer
Change subject’s pose using a reference image.  

### 🔹 History
Keep track of all creations, re-download or clear history.  

---

## ⚙️ Project Structure
```
.
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

---

## 🌟 Future Improvements
- Support for **inpainting / masking edits**  
- Multiple image outputs per generation  
- Style presets (e.g., *photorealistic*, *anime*, *sketch*)  
- Cloud storage for history  

---

