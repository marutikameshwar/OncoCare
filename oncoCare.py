import streamlit as st
import os
from PyPDF2 import PdfReader
from PIL import Image
import google.generativeai as genai
os.environ["GOOGLE_API_KEY"]="AIzaSyAu-M58xYzHpu1_e_XORAYS_GZ3gf2U1xE"

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("🚨 GOOGLE_API_KEY not set. Please export it before running the app.")
else:
    genai.configure(api_key=api_key)
    model =  genai.GenerativeModel("gemini-2.5-flash")

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def process_uploaded_files(uploaded_files):
    text_data = []
    image_data = []

    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            text_data.append(extract_text_from_pdf(uploaded_file))
        elif uploaded_file.type.startswith("text/"):
            text_data.append(uploaded_file.read().decode("utf-8"))
        elif uploaded_file.type.startswith("image/"):
            image = Image.open(uploaded_file)
            image_data.append(image)
            # For scans: send image + text together
            text_data.append("[Image scan uploaded. Needs imaging analysis.]")
        else:
            text_data.append(f"[Unsupported file type: {uploaded_file.type}]")

    return "\n".join(text_data), image_data

def query_gemini(user_prompt: str) -> str:
    try:
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"❌ Error querying Gemini: {e}"


def main():
    st.title("🧬 OncoCare - AI-Enhanced Oncology Analysis Platform")
    st.markdown("""
        ### A Clinical Decision Support Tool for Oncology Professionals
        
        This platform demonstrates the potential of AI-assisted analysis in oncology practice:
        - Rapid analysis of medical reports and imaging
        - Structured patient health summaries
        - Evidence-based dietary and supportive care recommendations
        - Comprehensive treatment impact assessment
        
        Upload patient reports to see how AI can assist in synthesizing clinical information.
        """)

    uploaded_files = st.file_uploader(
        "Upload sample medical files for analysis demonstration",
        type=["pdf", "txt", "jpg", "png", "jpeg"],
        accept_multiple_files=True
    )
    st.info("💡 This prototype demonstrates AI capabilities in analyzing medical reports and generating structured summaries to assist healthcare professionals in their workflow.")

    if uploaded_files:
        with st.spinner("Processing files..."):
            combined_text, images = process_uploaded_files(uploaded_files)

        st.success("Files processed successfully ✅")
        st.info("This analysis is meant to demonstrate AI capabilities in clinical support. Always refer to your clinical judgment and established protocols for patient care.")

        if st.button("Generate Analysis Report"):
            st.subheader("📋 Cancer Status Summary")
            st.write(query_gemini(f"Conduct a comprehensive oncological analysis following industry standards: 1) TNM Classification and staging 2) Histopathological analysis including molecular markers if present 3) Radiological findings with specific measurements and progression criteria (RECIST if applicable) 4) Key laboratory values and their clinical significance 5) Disease progression indicators 6) Metastatic status assessment. Utilize standard medical reporting formats and terminology. Reference source data:\n{combined_text}"))

            st.subheader("💡 Overall Health Report")
            st.write(query_gemini(f"Generate a systematic clinical evaluation following standard medical protocols: 1) ECOG/Karnofsky performance status 2) Vital signs trend analysis 3) Complete blood count interpretation 4) Organ function assessment (hepatic, renal, cardiac) 5) Key oncological markers and their temporal trends 6) Comprehensive metabolic panel analysis 7) Documented adverse events (CTCAE grading) 8) Quality of life indicators. Analyze clinical data from:\n{combined_text}"))

            st.subheader("🥗 Recommended Diet")
            st.write(query_gemini(f"Perform a detailed nutritional assessment following ESPEN/ASPEN guidelines: 1) Anthropometric measurements analysis 2) Nutritional risk screening (NRS 2002) 3) Current BMI and weight change trends 4) Macro and micronutrient requirements based on disease state 5) Treatment-specific dietary modifications 6) Malnutrition risk assessment 7) Specific dietary restrictions based on organ function 8) Interaction with current treatment protocol. Analysis based on clinical data from:\n{combined_text}"))

            st.subheader("💊 Medication Plan")
            st.write(query_gemini(f"Conduct a comprehensive treatment protocol analysis following NCCN/ASCO guidelines: 1) Current treatment regimen evaluation 2) Response assessment using standard criteria (RECIST/WHO) 3) Toxicity profile analysis (using CTCAE criteria) 4) Drug interaction assessment 5) Supportive care requirements based on documented symptoms 6) Standard prophylaxis recommendations 7) Treatment compliance analysis 8) Next phase treatment considerations based on response. Note: This is a clinical analysis tool, not prescriptive advice. Analysis derived from:\n{combined_text}"))

            st.subheader("📂 Uploaded Files Content (Preview)")
            st.text_area("Extracted Data", combined_text, height=200)

            if images:
                st.subheader("🖼 Uploaded Scans")
                for img in images:
                    st.image(img, caption="Medical Scan")

if __name__ == "__main__":
    main()
