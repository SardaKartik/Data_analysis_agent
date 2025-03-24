import streamlit as st
import os
import time
from pathlib import Path
from data_agent import run_agent  # Importing agent kickoff crew

def agent_kartik(csv_file, user_name, folder_name):
    # Save CSV file temporarily
    csv_path = os.path.join("temp", csv_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(csv_path, "wb") as f:
        f.write(csv_file.getbuffer())
    
    # Run the agent kickoff
    data_analysis_crew.kickoff()

st.title("Streamlit File Downloader")

# User inputs
csv_file = st.file_uploader("Upload a CSV file:", type=["csv"])
user_name = st.text_input("Enter your name:", "")
folder_name = st.text_input("Enter the output folder name:", "")

if st.button("Generate Files"):
    if csv_file and user_name:
        agent_kartik(csv_file, user_name, folder_name)
        
        # Simulate processing delay
        time.sleep(3)  # 3-second delay before showing download options
        
        # Generate file paths based on user name using os.getcwd()
        base_dir = os.getcwd()
        base_path = os.path.join(base_dir, user_name)
        st.session_state["output_files"] = {
            "File 1": f"{base_path}_anomaly_detection_report.md",
            "File 2": f"{base_path}_statistical_analysis_report.md",
            "File 3": f"{base_path}_visualization_report.md",
        }
        st.session_state["files_ready"] = True
        st.success(f"Files are ready for {user_name}!")
    else:
        st.warning("Please provide all required inputs before generating files.")

# Display download buttons if files are ready
if st.session_state.get("files_ready", False):
    for file_label, file_path in st.session_state["output_files"].items():
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file_label}",
                    data=f,
                    file_name=Path(file_path).name,
                    mime="application/octet-stream"
                )
        else:
            st.warning(f"{file_label} not found at {file_path}")
