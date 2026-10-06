import logging
from datetime import datetime

import streamlit as st

from utils import read_yaml, setup_logging
from preprocess import read_image, extract_id_card, save_image
from ocr_engine import extract_text
from postprocess import extract_information
from face_verification import detect_and_extract_face, face_comparison, get_face_embeddings
from mysqldb_operations import insert_records, fetch_records

# {
#   "ID": "CCNPA",
#   "Name": "BIBEK RAUTH",
#   "Father's Name": "AJAY RAUTH",
#   "DOB": "14/09/1994",
#   "ID Type": "PAN"
# }

setup_logging()

config = read_yaml("config.yaml")
INTERMEDIATE_DIR = config["artifacts"]["INTERMIDEIATE_DIR"]


# Set wider page layout
def wider_page():
    max_width_str = "max-width: 1200px;"
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{ {max_width_str} }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    logging.info("Page layout set to wider configuration.")

# Customized Streamlit theme
def set_custom_theme():
    st.markdown(
        """
        <style>
            body {
                background-color: #f0f2f6; /* Set background color */
                color: #333333; /* Set text color */
            }
            .sidebar .sidebar-content {
                background-color: #ffffff; /* Set sidebar background color */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    logging.info("Custom theme applied to Streamlit app.")

# Sidebar
def sidebar_section():
    st.sidebar.title("Select ID Card Type")
    option = st.sidebar.selectbox("ID card type", ("PAN",), label_visibility="collapsed")
    logging.info(f"ID card type selected: {option}")
    return option

# Header
def header_section(option):
    if option == "Aadhar":
        st.title("Registration Using Aadhar Card")
        logging.info("Header set for Aadhar Card registration.")
    elif option == "PAN":
        st.title("Registration Using PAN Card")
        logging.info("Header set for PAN Card registration.")

# Main content
def main_content(image_file, face_image_file):
    if image_file is None:
        st.warning("Please upload an ID card image.")
        logging.warning("No ID card image uploaded.")
        return

    if face_image_file is None:
        st.info("Now upload a clear face image (selfie) to continue.")
        return

    face_image = read_image(face_image_file, is_uploaded=True)
    if face_image is None:
        st.error("Could not read the face image. Please upload a valid JPG/PNG image.")
        logging.error("Face image could not be read.")
        return
    logging.info("Face image loaded.")

    image = read_image(image_file, is_uploaded=True)
    if image is None:
        st.error("Could not read the ID card image. Please upload a valid JPG/PNG image.")
        logging.error("ID card image could not be read.")
        return
    logging.info("ID card image loaded.")

    image_roi, _ = extract_id_card(image)
    if image_roi is None:
        st.error("Could not detect an ID card in the image. Please upload a clearer photo.")
        return
    logging.info("ID card ROI extracted.")

    face_image_path2 = detect_and_extract_face(img=image_roi)
    if face_image_path2 is None:
        st.error("No face was found on the ID card. Please upload a clearer ID card image.")
        return
    face_image_path1 = save_image(face_image, "face_image.jpg", path=INTERMEDIATE_DIR)
    logging.info("Faces extracted and saved.")

    with st.spinner("Comparing faces (first run downloads/loads models, please wait)..."):
        is_face_verified = face_comparison(image1_path=face_image_path1, image2_path=face_image_path2)
    logging.info(f"Face verification status: {'successful' if is_face_verified else 'failed'}.")

    if not is_face_verified:
        st.error("Face verification failed. Please try again.")
        return

    st.success("Face verification successful.")

    with st.spinner("Reading text from the ID card..."):
        extracted_text = extract_text(image_roi)
    text_info = extract_information(extracted_text)
    logging.info("Text extracted and information parsed from ID card.")

    if not text_info["ID"] or not isinstance(text_info["DOB"], datetime):
        st.error("Could not read the required fields (ID, DOB) from the ID card. "
                 "Please upload a clearer, straight, well-lit image.")
        with st.expander("Raw OCR output"):
            st.write(extracted_text)
        return

    try:
        records = fetch_records(text_info)
        if records.shape[0] > 0:
            st.warning(f"User already present with ID {text_info['ID']}")
            st.dataframe(records.drop(columns=["embedding"], errors="ignore"))
            return

        st.write(text_info)
        text_info['DOB'] = text_info['DOB'].strftime('%Y-%m-%d')
        text_info['Embedding'] = get_face_embeddings(face_image_path1)
        insert_records(text_info)
        st.success(f"New user registered with ID {text_info['ID']}")
        logging.info(f"New user record inserted: {text_info['ID']}")
    except Exception as e:
        logging.exception("Database operation failed")
        st.error(f"Database error: {e}")

# Main function setup as previously provided...
def main():
    wider_page()
    set_custom_theme()
    option = sidebar_section()
    header_section(option)
    image_file = st.file_uploader("Upload ID Card", type=["jpg", "jpeg", "png", "webp"])
    face_image_file = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png", "webp"])
    main_content(image_file, face_image_file)

if __name__ == "__main__":
    main()
