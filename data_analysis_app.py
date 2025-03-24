import streamlit as st
import pandas as pd
import os
import time
from Data_analysisi_agent import data_analysis_crew

def save_uploaded_file(uploaded_file):
    """Save the uploaded file temporarily"""
    file_path = os.path.join("temp_data.csv")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.title("🔍 Data Analysis AI Agent")
st.write("Upload a CSV file for automated data analysis, anomaly detection, and visualization.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    file_path = save_uploaded_file(uploaded_file)
    df = pd.read_csv(file_path)
    
    st.write("### Uploaded Data Preview:")
    st.dataframe(df)

    # Run the analysis
    if st.button("Analyze Data"):
        with st.spinner("Running AI-powered analysis..."):
            result = data_analysis_crew.kickoff()

        st.write("### Analysis Completed ✅")
        
        # Find the generated report files
        report_files = [f for f in os.listdir() if f.endswith(".md") or f.endswith(".png")]

        # Display Markdown reports and provide download links
        for report in report_files:
            file_path = os.path.join(report)
            
            # Show Markdown content in browser
            if report.endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                st.write(f"#### 📄 {report}")
                st.markdown(content)

            # Provide download button
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {report}",
                    data=f,
                    file_name=report,
                    mime="text/markdown" if report.endswith(".md") else "image/png"
                )
