import streamlit as st
from supabase_config import supabase
from ml_model import predict_category
from PIL import Image
import uuid
import io
from datetime import datetime

st.set_page_config(page_title="Digitale Fundkiste")

st.title("📦 Digitale Fundkiste")

page = st.radio("Navigation", ["Start", "Eintrag erstellen", "Suchen"])


# START

if page == "Start":

    st.write("Willkommen bei der digitalen Fundkiste.")


# EINTRAG ERSTELLEN

elif page == "Eintrag erstellen":

    typ = st.selectbox("Typ", ["gefunden", "gesucht"])

    uploaded_file = st.file_uploader(
        "Bild hochladen",
        type=["jpg", "jpeg", "png"]
    )

    beschreibung = st.text_area("Beschreibung")

    kategorie = "Sonstiges"

    if uploaded_file:

        image = Image.open(uploaded_file).convert("RGB")

        st.image(image, width=300)

        try:
            kategorie = predict_category(image)
            st.success(f"Kategorie erkannt: {kategorie}")
        except Exception as e:
            st.warning("Kategorie konnte nicht erkannt werden")

    if st.button("Speichern"):

        if uploaded_file is None:
            st.error("Bitte ein Bild hochladen")
            st.stop()

        filename = f"{uuid.uuid4()}.jpg"

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")

        try:

            supabase.storage.from_("images").upload(
                path=filename,
                file=image_bytes.getvalue(),
                file_options={"content-type": "image/jpeg"}
            )

            public_url = supabase.storage.from_("images").get_public_url(filename)

            supabase.table("fundkiste").insert({
                "bild_url": public_url,
                "kategorie": kategorie,
                "beschreibung": beschreibung,
                "typ": typ,
                "datum": datetime.now().date().isoformat()
            }).execute()

            st.success("Eintrag erfolgreich gespeichert!")

        except Exception as e:
            st.error("Fehler beim Speichern")


# SUCHE

elif page == "Suchen":

    filter_typ = st.selectbox("Typ auswählen", ["gefunden", "gesucht"])

    data = supabase.table("fundkiste").select("*").execute()

    for eintrag in data.data:

        if eintrag["typ"] != filter_typ:
            continue

        st.image(eintrag["bild_url"], width=200)

        st.write("Kategorie:", eintrag["kategorie"])
        st.write("Beschreibung:", eintrag["beschreibung"])
        st.write("Datum:", eintrag["datum"])

        st.divider()
