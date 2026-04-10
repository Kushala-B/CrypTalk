import streamlit as st
import requests
from deep_translator import GoogleTranslator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zlib
import time

# 🔗 Backend URL
BACKEND_URL = "https://cryptalk-2.onrender.com/get"

# 🌍 Language codes
LANG = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml"
}

# 😊 Emoji mapping (FIXED)
EMOJI_MAP = {
    "joy": "😊",
    "sadness": "😢",
    "anger": "😠",
    "fear": "😨",
    "surprise": "😲",
    "neutral": "😐",
    "confusion": "😕",
    "question": "❓"
}

# 🔐 Decryption
def decrypt(enc, key, nonce):
    aes = AESGCM(bytes.fromhex(key))
    return aes.decrypt(bytes.fromhex(nonce), bytes.fromhex(enc), None)

# 🎨 UI
st.set_page_config(page_title="CrypTalk Receiver", page_icon="📥")
st.title("📥 CrypTalk Receiver")

chosen_lang = st.selectbox("Choose Output Language", list(LANG.keys()))

# 🔄 Wake backend button
if st.button("🔄 Wake Backend"):
    try:
        requests.get(BACKEND_URL)
        st.success("Backend pinged. Wait 10–20 seconds.")
    except:
        st.warning("Backend still waking up...")

# 📥 Receive message
if st.button("Receive Message"):

    st.info("Connecting to server... please wait")

    data = None

    # 🔁 Retry logic
    for i in range(10):
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

        except:
            st.write("Still trying to connect...")
            time.sleep(3)

    if not data or "encrypted" not in data:
        st.error("❌ Backend still sleeping OR no message found")
        st.stop()

    # 🔐 Decrypt
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

    # 🧠 Emotion detection (FIXED)
    emotion_word = data["emotion"].split()[0].lower()

    # 💡 Detect question
    if "?" in msg:
        emotion_word = "question"

    # 😊 Get emoji
    emoji = EMOJI_MAP.get(emotion_word, "💬")

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
