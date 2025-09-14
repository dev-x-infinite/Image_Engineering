import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from datetime import datetime

# --------------------------
# Page config + lightweight styling
# --------------------------
st.set_page_config(
    page_title="AI Image Generator & Editor",
    page_icon="🖼️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
/* Layout polish */
.block-container { padding-top: 1rem; }
h1, h2, h3 { letter-spacing: .2px; }
.card {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.preview {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.75rem;
    background: #eef2ff;
    color: #3730a3;
    margin-left: .5rem;
}
.small { color: #6b7280; font-size: 0.9rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------------
# Session state
# --------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {"bytes": b, "mime": str, "meta": {...}}

# --------------------------
# Helpers
# --------------------------
@st.cache_resource(show_spinner=False)
def make_client(api_key: str):
    return genai.Client(api_key=api_key)

def extract_images(response):
    images = []
    try:
        candidate = response.candidates[0]
        for part in candidate.content.parts:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                images.append((part.inline_data.data, part.inline_data.mime_type))
    except Exception as e:
        st.error("No image data found in model response. Try adjusting your prompt.")
    return images

def add_to_history(img_bytes: bytes, mime: str, kind: str, prompt: str):
    meta = {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kind": kind,
        "prompt": prompt,
    }
    st.session_state.history.append({"bytes": img_bytes, "mime": mime, "meta": meta})

def show_images(images, base_filename: str, caption: str):
    for idx, (img_bytes, mime) in enumerate(images, start=1):
        img = Image.open(BytesIO(img_bytes))
        st.image(img, caption=f"{caption} #{idx}", use_column_width=True)
        st.download_button(
            "Download",
            data=img_bytes,
            file_name=f"{base_filename}_{idx}.{ 'png' if 'png' in mime else 'jpg' }",
            mime=mime,
            key=f"download_{base_filename}_{idx}_{len(st.session_state.history)}",
        )

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown(
        "Use Streamlit Secrets or paste your key below. "
        "Tip: set `GOOGLE_API_KEY` in `.streamlit/secrets.toml`."
    )
    default_key = st.secrets.get("GOOGLE_API_KEY", "")
    api_key = st.text_input("Google API Key", type="password", value=default_key, placeholder="Paste your key…")

    st.markdown("Models")
    text_model = st.selectbox(
        "Text model (for prompt enhancement & pose description)",
        ["gemini-1.5-flash"],
        index=0,
    )
    image_model = st.selectbox(
        "Image model",
        ["gemini-2.5-flash-image-preview"],
        index=0,
    )

    enhance_prompts = st.checkbox("Enhance prompts automatically", value=False)
    st.caption("Enhancement helps add details (lighting, style, composition).")

    st.divider()
    with st.expander("Help"):
        st.markdown(
            "- Text → Image: Generate new images from a prompt.\n"
            "- Simple Edit: Upload an image and describe changes.\n"
            "- Pose Transfer: Give a base image and a reference pose image.\n"
            "- History: Browse, download, and reuse previous results."
        )
        st.markdown(
            "<span class='small'>Note: The preview image model can change over time.</span>",
            unsafe_allow_html=True,
        )

# --------------------------
# Header
# --------------------------
st.title("🖼️ AI Image Generator & Editor")
st.markdown(
    "Create, edit, and transform images with Gemini."
    " <span class='badge'>Preview</span>",
    unsafe_allow_html=True,
)
st.write("")

# Guard for API key
if not api_key:
    st.warning("Add your Google API key in the sidebar to start.")
    st.stop()

# Build client
try:
    client = make_client(api_key)
except Exception as e:
    st.error("Failed to initialize Gemini client. Check your API key.")
    st.stop()

# --------------------------
# Tabs
# --------------------------
tab_gen, tab_edit, tab_pose, tab_hist = st.tabs(
    ["Text → Image", "Simple Edit", "Pose Transfer", "History"]
)

# --- TEXT TO IMAGE ---
with tab_gen:
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.header("Text → Image")
        prompt = st.text_area("Enter your prompt", height=140, placeholder="A cinematic portrait of a cyberpunk explorer at night under neon rain...")
        gen_btn = st.button("Generate Image", type="primary")

    with col2:
        st.markdown("### Output")
        out_container = st.container()

    if gen_btn:
        if not prompt.strip():
            st.error("Please enter a prompt.")
        else:
            final_prompt = prompt
            if enhance_prompts:
                with st.spinner("Enhancing prompt…"):
                    try:
                        enhance_response = client.models.generate_content(
                            model=text_model,
                            contents=[f"Improve this prompt for high-quality image generation. Keep it concise but vivid. Prompt: {prompt}"]
                        )
                        final_prompt = enhance_response.candidates[0].content.parts[0].text
                        st.toast("Prompt enhanced ✨")
                    except Exception as e:
                        st.warning("Prompt enhancement failed. Using original prompt.")
                        final_prompt = prompt

                st.markdown("**Enhanced Prompt**")
                st.code(final_prompt)

            with st.spinner("Generating image…"):
                try:
                    response = client.models.generate_content(
                        model=image_model,
                        contents=[final_prompt],
                    )
                    images = extract_images(response)
                    if images:
                        with out_container:
                            show_images(images, "generated_image", "Generated Image")
                            for img_bytes, mime in images:
                                add_to_history(img_bytes, mime, "Text→Image", final_prompt)
                        st.balloons()
                    else:
                        st.error("No image returned. Try a more specific prompt.")
                except Exception as e:
                    st.error(f"Generation error: {e}")

# --- SIMPLE EDIT ---
with tab_edit:
    st.header("Simple Edit")
    col1, col2 = st.columns([0.55, 0.45])

    with col1:
        uploaded_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        edit_prompt = st.text_area("Describe the edit", height=120, placeholder="Make the sky dramatic with orange and purple clouds; add soft rim lighting…")
        edit_btn = st.button("Apply Edit", type="primary")

    with col2:
        st.markdown("### Output")
        out_container_edit = st.container()

    if edit_btn:
        if not uploaded_img:
            st.error("Please upload an image to edit.")
        elif not edit_prompt.strip():
            st.error("Please enter edit instructions.")
        else:
            image = Image.open(uploaded_img)
            final_edit_prompt = edit_prompt

            if enhance_prompts:
                with st.spinner("Enhancing edit prompt…"):
                    try:
                        enhance_edit = client.models.generate_content(
                            model=text_model,
                            contents=[f"Improve this instruction for image editing. Keep it actionable, concise, and visual. Instruction: {edit_prompt}"]
                        )
                        final_edit_prompt = enhance_edit.candidates[0].content.parts[0].text
                        st.toast("Edit prompt enhanced ✨")
                    except Exception as e:
                        st.warning("Enhancement failed. Using original instruction.")
                        final_edit_prompt = edit_prompt

                st.markdown("**Enhanced Edit Prompt**")
                st.code(final_edit_prompt)

            with st.spinner("Editing image…"):
                try:
                    response = client.models.generate_content(
                        model=image_model,
                        contents=[final_edit_prompt, image],
                    )
                    images = extract_images(response)
                    if images:
                        with out_container_edit:
                            show_images(images, "edited_image", "Edited Image")
                            for img_bytes, mime in images:
                                add_to_history(img_bytes, mime, "Simple Edit", final_edit_prompt)
                        st.toast("Edit complete ✅")
                    else:
                        st.error("No edited image returned. Try more precise instructions.")
                except Exception as e:
                    st.error(f"Edit error: {e}")

# --- POSE TRANSFER ---
with tab_pose:
    st.header("Pose Transfer")
    col1, col2 = st.columns([0.55, 0.45])

    with col1:
        base_img = st.file_uploader("Upload base image", type=["png", "jpg", "jpeg"], key="pose_base")
        ref_img = st.file_uploader("Upload reference pose image", type=["png", "jpg", "jpeg"], key="pose_ref")
        pose_btn = st.button("Apply Pose Transfer", type="primary")

    with col2:
        st.markdown("### Output")
        out_container_pose = st.container()

    if pose_btn:
        if not base_img or not ref_img:
            st.error("Please upload both the base image and the reference pose image.")
        else:
            img1 = Image.open(base_img)
            img2 = Image.open(ref_img)

            with st.spinner("Extracting pose from reference…"):
                try:
                    pose_response = client.models.generate_content(
                        model=text_model,
                        contents=["Describe the pose in this image for use as an editing instruction.", img2],
                    )
                    pose_prompt = pose_response.candidates[0].content.parts[0].text
                    st.markdown("**Extracted Pose Prompt**")
                    st.code(pose_prompt)
                except Exception as e:
                    st.error(f"Pose extraction failed: {e}")
                    pose_prompt = None

            if pose_prompt:
                with st.spinner("Applying pose to base image…"):
                    try:
                        response = client.models.generate_content(
                            model=image_model,
                            contents=[f"Change the pose of this person as described: {pose_prompt}", img1],
                        )
                        images = extract_images(response)
                        if images:
                            with out_container_pose:
                                show_images(images, "pose_transfer", "Pose Transferred Image")
                                for img_bytes, mime in images:
                                    add_to_history(img_bytes, mime, "Pose Transfer", pose_prompt)
                            st.toast("Pose transfer complete ✅")
                        else:
                            st.error("No result image returned. Try a clearer reference pose.")
                    except Exception as e:
                        st.error(f"Pose transfer error: {e}")

# --- HISTORY ---
with tab_hist:
    st.header("History")
    if not st.session_state.history:
        st.info("No images yet. Generate, edit, or transfer a pose to see your history here.")
    else:
        cols = st.columns(3)
        for i, entry in enumerate(reversed(st.session_state.history)):
            img = Image.open(BytesIO(entry["bytes"]))
            with cols[i % 3]:
                with st.container():
                    st.image(img, use_column_width=True, caption=f"{entry['meta']['kind']} • {entry['meta']['ts']}", output_format="PNG")
                    st.caption(f"Prompt: {entry['meta']['prompt'][:120]}{'…' if len(entry['meta']['prompt'])>120 else ''}")
                    st.download_button(
                        "Download",
                        data=entry["bytes"],
                        file_name=f"{entry['meta']['kind'].replace(' ', '_').lower()}_{entry['meta']['ts'].replace(':','-')}.png",
                        mime=entry["mime"],
                        key=f"hist_dl_{i}",
                    )

        st.divider()
        if st.button("Clear history"):
            st.session_state.history.clear()
            st.experimental_rerun()