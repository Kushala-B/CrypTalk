import streamlit as st
import requests
from deep_translator import GoogleTranslator
import zlib, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 🔑 PUT YOUR OPENROUTER API KEY HERE
OPENROUTER_API_KEY = "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"
BACKEND_URL = "https://cryptalk-2.onrender.com/send"

# 🌍 Languages (UPDATED)
LANG = {
    "English":"en",
    "Hindi":"hi",
    "Kannada":"kn",
    "Tamil":"ta",
    "Telugu":"te",
    "Malayalam":"ml"
}

# 😊 Emoji map (UPDATED)
EMOJI = {
    "joy":"😊",
    "sadness":"😢",
    "anger":"😠",
    "fear":"😨",
    "surprise":"😲",
    "confusion":"😕",
    "neutral":"😐"
}

# 🔥 SMART EMOTION DETECTION (LLM)
def detect_emotion(text):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Identify the emotion of this sentence.
    Only return ONE word from:
    joy, sadness, anger, fear, surprise, confusion, neutral.

    Sentence: "{text}"
    """

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        emotion = result["choices"][0]["message"]["content"].strip().lower()
        return emotion
    except:
        return "neutral"

# 🔐 Encryption
def encrypt(data):
    key = AESGCM.generate_key(bit_length=128)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, data, None)
    return encrypted, key, nonce

# UI
st.title("📤 CrypTalk Sender")

sender = st.text_input("Sender")
receiver = st.text_input("Receiver")

s_lang = st.selectbox("Sender Language", list(LANG.keys()))
r_lang = st.selectbox("Receiver Language", list(LANG.keys()))

msg = st.text_area("Message")

if st.button("Send"):
    if not msg.strip():
        st.warning("Enter message")
    else:
        translated = GoogleTranslator(
            source=LANG[s_lang],
            target="en"
        ).translate(msg)

        # 🔥 Emotion detection
        emotion = detect_emotion(translated)
        emoji = EMOJI.get(emotion, "💬")

        tagged = f"[{emotion.upper()} {emoji}] {translated}"

        compressed = zlib.compress(tagged.encode())
        enc, key, nonce = encrypt(compressed)

        payload = {
            "sender": sender,
            "receiver": receiver,
            "sender_lang": s_lang,
            "receiver_lang": r_lang,
            "emotion": emotion,
            "encrypted": enc.hex(),
            "key": key.hex(),
            "nonce": nonce.hex(),
            "tagged_text": tagged
        }

        res = requests.post(BACKEND_URL, json=payload)

        if res.status_code == 200:
            st.success("✅ Message Sent")
            st.write(tagged)
        else:
            st.error("Error sending")
