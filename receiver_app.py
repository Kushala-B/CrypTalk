import streamlit as st
import requests
from deep_translator import GoogleTranslator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zlib
import time

BACKEND_URL = "https://cryptalk-2.onrender.com/get"

LANG = {
    "English":"en",
    "Hindi":"hi",
    "Kannada":"kn",
    "Tamil":"ta",
    "Telugu":"te",
    "Malayalam":"ml"
}

def decrypt(enc,key,nonce):
    aes = AESGCM(bytes.fromhex(key))
    return aes.decrypt(bytes.fromhex(nonce), bytes.fromhex(enc), None)

st.title("📥 CrypTalk Receiver")

chosen_lang = st.selectbox("Choose Output Language", list(LANG.keys()))

if st.button("Receive Message"):

    st.info("Connecting to server... (wait if first time)")

    data = None

    # 🔁 Retry logic (for Render sleep)
    for i in range(3):
        try:
            res = requests.get(BACKEND_URL)

            if res.status_code != 200:
                st.error("❌ Backend error")
                st.write(res.text)
                st.stop()

            data = res.json()
            break

        except:
            time.sleep(3)

    if not data:
        st.error("❌ Could not connect to backend (maybe sleeping)")
        st.stop()

    if "encrypted" not in data:
        st.warning("⚠️ No message found. Send message first.")
        st.write(data)
        st.stop()

    try:
        dec = decrypt(data["encrypted"], data["key"], data["nonce"])
        text = zlib.decompress(dec).decode()
    except Exception as e:
        st.error("❌ Decryption failed")
        st.write(e)
        st.stop()

    # Split tag + message
    if "] " in text:
        tag, msg = text.split("] ", 1)
    else:
        tag, msg = "", text

    # Extract emotion + emoji
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

    st.success("✅ Message Received")

    st.write("Sender:", data["sender"])
    st.write("Emotion:", data["emotion"])

    st.write("📩 Final Output:")
    st.code(f"[{translated_emotion} {emoji}] {translated_msg}")
