import streamlit as st
import requests
from deep_translator import GoogleTranslator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zlib
import time

# 🔗 YOUR BACKEND
BACKEND_URL = "https://cryptalk-2.onrender.com/get"

# 🌍 Languages
LANG = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml"
}

# 🔐 Decrypt function
def decrypt(enc, key, nonce):
    aes = AESGCM(bytes.fromhex(key))
    return aes.decrypt(bytes.fromhex(nonce), bytes.fromhex(enc), None)

# 🎨 UI
st.set_page_config(page_title="CrypTalk Receiver", page_icon="📥")
st.title("📥 CrypTalk Receiver")

chosen_lang = st.selectbox("Choose Output Language", list(LANG.keys()))

# 🔘 Optional wake button
if st.button("🔄 Wake Backend"):
    try:
        requests.get(BACKEND_URL)
        st.success("Backend pinged. Wait 10–20 seconds.")
    except:
        st.warning("Backend still waking up...")

# 📥 Receive button
if st.button("Receive Message"):

    st.info("Connecting to server... please wait")

    data = None

    # 🔁 Retry loop (IMPORTANT FIX)
    for i in range(10):  # tries for ~30 seconds
        try:
            res = requests.get(BACKEND_URL, timeout=10)

            if res.status_code == 200:
                try:
                    data = res.json()
                except:
                    st.write("Invalid response, retrying...")
                    time.sleep(3)
                    continue

                if "encrypted" in data:
                    break

            st.write(f"Retrying... {i+1}/10")
            time.sleep(3)

        except Exception as e:
            st.write("Still trying to connect...")
            time.sleep(3)

    # ❌ If still no data
    if not data or "encrypted" not in data:
        st.error("❌ Backend still sleeping OR no message found")
        st.stop()

    # 🔐 Decrypt + decompress
    try:
        decrypted = decrypt(data["encrypted"], data["key"], data["nonce"])
        text = zlib.decompress(decrypted).decode()
    except Exception as e:
        st.error("❌ Failed to decrypt message")
        st.write(e)
        st.stop()

    # ✂️ Split tag + message
    if "] " in text:
        tag, msg = text.split("] ", 1)
    else:
        tag, msg = "", text

    # 😊 Emotion split
    emotion_parts = data["emotion"].split()
    emotion_word = emotion_parts[0]
    emoji = emotion_parts[1] if len(emotion_parts) > 1 else ""

    # 🌍 Translate message
    translated_msg = GoogleTranslator(
        source="en",
        target=LANG[chosen_lang]
    ).translate(msg)

    # 🌍 Translate emotion
    translated_emotion = GoogleTranslator(
        source="en",
        target=LANG[chosen_lang]
    ).translate(emotion_word)

    # ✅ Output
    st.success("✅ Message Received")

    st.write("👤 Sender:", data["sender"])
    st.write("💬 Original Emotion:", data["emotion"])

    st.write("📩 Final Output:")
    st.code(f"[{translated_emotion} {emoji}] {translated_msg}")
