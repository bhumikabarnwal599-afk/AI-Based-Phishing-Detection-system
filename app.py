from openai import OpenAI

client = OpenAI(api_key="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")

import streamlit as st
import joblib
import pandas as pd
import re
from PIL import Image


st.set_page_config(
    page_title="Phish Gaurd",
    page_icon="🛡️",
    layout="wide"
)

model = joblib.load("text_model.pkl")
url_model = joblib.load("url_model.pkl")
vectorizer = joblib.load("text_vectorizer.pkl")
url_vectorizer = joblib.load("url_vectorizer.pkl")



def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\W', ' ', text)
    return text


def predict_phishing(text):
    def contains_url(text):
        return "http" in text or "www" in text

    def predict_phishing(text):
        text_clean = clean_text(text)

        # TEXT PREDICTION
        text_vec = vectorizer.transform([text_clean])
        text_pred = model.predict(text_vec)[0]

        # URL PREDICTION (only if URL exists)
        if contains_url(text):
            url_vec = url_vectorizer.transform([text])
            url_pred = url_model.predict(url_vec)[0]
        else:
            url_pred = 0  # assume safe if no URL

        # FINAL SCORE
        score = (text_pred + url_pred) / 2

        if score == 0:
            return "🟢 Safe"
        elif score < 1:
            return "🟡 Suspicious"
        else:
            return "🔴 Phishing"

def get_confidence(text):
    text_clean = clean_text(text)
    vec = vectorizer.transform([text_clean])
    prob = model.predict_proba(vec)[0][1]
    return round(prob, 2)


def highlight_words(text):
    suspicious_words = ['win', 'free', 'urgent', 'click', 'offer', 'prize', 'lottery']
    found = [w for w in suspicious_words if w in text.lower()]
    return found

from PyPDF2 import PdfReader

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text

st.sidebar.title("🛡️ Phishing Detector")
st.sidebar.write("AI-Based Phishing Detection System")

menu = st.sidebar.selectbox("Navigation", ["🏠 Home", "📧 Email/SMS", "🌐 URL", "📄 PDF Scan", "📊 About","🤖 Ask with AI"])

import base64


def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)
set_bg("imgphishing.jpeg")
st.markdown("""
<style>
.block-container {
    background: rgba(255, 255, 255, 0.6);
    padding: 20px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
if menu == "🏠 Home":
    if menu == "🏠 Home":
        st.markdown('<div class="title">🛡️ AI Phishing Detection System</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Smart Cybersecurity Tool to Detect Phishing Attacks in Real-Time</div>',
                    unsafe_allow_html=True)

        st.write("")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="card">
            <h3>📧 Email/SMS Detection</h3>
            <p>Analyze messages and detect phishing content instantly.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="card">
            <h3>🌐 URL Scanner</h3>
            <p>Check if a link is safe or malicious before clicking.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="card">
            <h3>📂 Batch Processing</h3>
            <p>Upload files and scan multiple messages at once.</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        st.success("🚀 Built using Machine Learning + NLP + Streamlit")
elif menu == "📧 Email/SMS":

    st.markdown("## 📧 Email & SMS Scanner")

    user_input = st.text_area("✉️ Enter your message here...")

    if st.button("🔍 Analyze Message"):
        if user_input.strip() == "":
            st.warning("⚠️ Please enter some text")
        else:
            result = predict_phishing(user_input)

            if "Safe" in result:
                st.success(result)
            elif "Suspicious" in result:
                st.warning(result)
            else:
                st.error(result)

elif menu == "🌐 URL":
    st.header("🌐 URL Detection")

    url = st.text_input("Enter URL")

    if st.button("Check URL"):
        if url.strip() == "":
            st.warning("⚠️ Enter URL")
        else:
            vec = url_vectorizer.transform([url])
            result = url_model.predict(vec)[0]

            if result == 1:
                st.error("🔴 Malicious URL")
            else:
                st.success("🟢 Safe URL")
elif menu == "📄 PDF Scan":
    st.header("📄 Upload PDF to Scan")

    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])

    if pdf_file:
        if st.button("🔍 Analyze PDF"):   # 👈 BUTTON

            with st.spinner("Analyzing PDF..."):

                text = extract_text_from_pdf(pdf_file)

                if text.strip() == "":
                    st.warning("⚠️ No readable text found in PDF")
                else:
                    result = predict_phishing(text)

                    if result == "🟢 Safe":
                        st.success("🟢 PDF is Safe")
                    elif result == "🟡 Suspicious":
                        st.warning("🟡 PDF is Suspicious")
                    else:
                        st.error("🔴 PDF is Malicious")


elif menu == "📊 About":
    st.header("📊 About Project")

    st.write("""
    
    This project uses Machine Learning to detect phishing attacks.

    🔹 Models Used:
    - Random Forest (Text)
    - Logistic Regression (URL)

    🔹 Techniques:
    - TF-IDF Vectorization
    - NLP Processing

    🔹 Developed by:
    ThinkShield
    """)
elif menu == "🤖 Ask with AI":
    st.header("🤖 Ask with AI (Phishing Assistant)")
    st.write("💬 Ask anything about phishing, scams & online safety")

    user_input = st.text_input("Type your question here...")

    if st.button("Ask"):

        query = user_input.lower()

        if "phishing" in query:
            st.success("Phishing ek cyber attack hai jisme attacker fake email, SMS ya website ke through user ka sensitive data chura leta hai.")

        elif "example" in query:
            st.success("Example: Fake bank message jisme likha hota hai 'Your account blocked, click here to verify' — ye phishing ho sakta hai.")

        elif "why" in query or "kyu" in query:
            st.success("Attackers phishing isliye karte hain taaki wo password, OTP, bank details ya paise chura saken.")


        elif "types" in query:
            st.success("Phishing ke types: Email phishing, SMS phishing (Smishing), Voice phishing (Vishing), Clone phishing.")

        elif "email phishing" in query:
            st.success("Email phishing me attacker fake emails bhejta hai jo original company jaise lagte hain.")

        elif "sms" in query or "smishing" in query:
            st.success("Smishing me attacker SMS ke through fake links bhejta hai.")

        elif "vishing" in query or "call" in query:
            st.success("Vishing me attacker phone call karke user ko manipulate karta hai.")

        elif "detect" in query or "identify" in query:
            st.success("Phishing detect karne ke liye: Suspicious links check karo, sender email verify karo, grammar mistakes dekho.")

        elif "link" in query:
            st.success("Fake links me spelling mistake hoti hai jaise 'amaz0n.com' instead of 'amazon.com'.")

        elif "email" in query:
            st.success("Unknown sender ya urgent tone wala email suspicious hota hai.")

        elif "safe" in query or "prevent" in query or "bach" in query:
            st.success("Safe rehne ke liye: Unknown links par click mat karo, OTP kisi ko share mat karo, 2FA enable karo.")

        elif "otp" in query:
            st.error("⚠️ OTP kabhi kisi ke sath share mat karo — even bank bhi nahi maangta!")

        elif "password" in query:
            st.success("Strong password use karo aur different accounts ke liye alag password rakho.")

        elif "bank" in query:
            st.warning("Bank kabhi bhi email/SMS se sensitive info nahi maangta.")

        elif "malware" in query:
            st.success("Phishing ke through malware install ho sakta hai jo device ko damage karta hai.")

        elif "url" in query:
            st.success("Always URL ko dhyan se check karo — https aur domain name verify karo.")

        elif "https" in query:
            st.success("HTTPS secure hota hai, lekin phishing site bhi https use kar sakti hai — sirf uspe depend mat karo.")

        else:
            st.info("🤖 Mujhe samajh nahi aaya. Try asking about phishing, safety, examples, OTP, links, etc.")