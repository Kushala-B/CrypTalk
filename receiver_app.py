import streamlit as st
import requests
from deep_translator import GoogleTranslator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zlib

BACKEND_URL = "https://cryptalk-jriee.onrender.com/get"

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

# 🔥 NEW: user can choose output language
chosen_lang = st.selectbox("Choose Output Language", list(LANG.keys()))

if st.button("Receive"):
    res = requests.get(BACKEND_URL)
    data = res.json()

    dec = decrypt(data["encrypted"], data["key"], data["nonce"])
    text = zlib.decompress(dec).decode()

    # Extract only message (remove tag)
    if "] " in text:
        tag, msg = text.split("] ", 1)
    else:
        tag, msg = "", text

    translated = GoogleTranslator(
        source="en",
        target=LANG[chosen_lang]
    ).translate(msg)

    st.write("Sender:", data["sender"])
    st.write("Emotion:", data["emotion"])
    st.write("Original:", text)
    st.write("Translated:", f"{tag}] {translated}" if tag else translated)
