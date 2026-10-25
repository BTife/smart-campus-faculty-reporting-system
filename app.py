"""Campus facility report form (v1: capture and save only, no AI yet)."""
import io
from pathlib import Path

import streamlit as st
from PIL import Image

from storage import save_report, using_azure

MAX_TEXT = 1000
MIN_TEXT = 10
MAX_PHOTO_MB = 5
# Replace with your campus's real buildings.
LOCATIONS = ["Not sure / not listed", "McMechen", "Calloway", "Graves", "CBEIS",
             "Library", "Cafeteria", "Sports complex", "Outdoor / grounds"]

st.set_page_config(page_title="Report a campus issue", page_icon="🛠️")
st.title("Report a campus issue")
st.caption("Describe what's wrong and where. A photo helps but is optional.")

if not using_azure():
    st.info("Local mode: reports are saved to ./local_data, not Azure.")

with st.form("report_form", clear_on_submit=True):
    text = st.text_area("What's the problem and where?", max_chars=MAX_TEXT,
                        placeholder="e.g. The AC in Block C room 204 is dripping water")
    location = st.selectbox("Building (optional)", LOCATIONS)
    photo = st.file_uploader("Add a photo (optional)", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Submit report")

if submitted:
    text = text.strip()
    photo_bytes, photo_ext, error = None, "", None

    if len(text) < MIN_TEXT:
        error = f"Please describe the problem (at least {MIN_TEXT} characters)."
    elif photo is not None:
        photo_bytes = photo.getvalue()
        photo_ext = Path(photo.name).suffix.lower()
        if len(photo_bytes) > MAX_PHOTO_MB * 1024 * 1024:
            error = f"Photo is too large. Maximum is {MAX_PHOTO_MB} MB."
        else:
            try:  # confirm it's a real image, not just a renamed file
                Image.open(io.BytesIO(photo_bytes)).verify()
            except Exception:
                error = "That file doesn't look like a valid image."

    if error:
        st.error(error)
    else:
        try:
            report_id = save_report(
                text,
                "" if location == LOCATIONS[0] else location,
                photo_bytes,
                photo_ext,
            )
            st.success(f"Report submitted. Thank you! Reference: {report_id[:8]}")
        except Exception as e:
            st.error("Something went wrong saving your report. Please try again.")
