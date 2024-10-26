import streamlit as st
from linkedin_api import Linkedin
import json
from datetime import datetime
import os
from typing import List, Dict

class LinkedInCustomFeed:
    # [La classe rimane identica a prima]
    # La inserisco qui ma nascosta per brevità
    pass

# Configurazione della pagina Streamlit
st.set_page_config(page_title="LinkedIn Custom Feed", page_icon="📱", layout="wide")

# Sidebar per login e gestione profili
with st.sidebar:
    st.title("📱 LinkedIn Custom Feed")
    
    # Login form
    st.subheader("Login")
    email = st.text_input("Email LinkedIn", type="default")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email and password:
            try:
                st.session_state.custom_feed = LinkedInCustomFeed(email, password)
                st.success("Login effettuato con successo!")
            except Exception as e:
                st.error(f"Errore durante il login: {e}")
    
    # Form per aggiungere nuovi profili
    st.subheader("Aggiungi Profilo")
    new_profile = st.text_input("URL Profilo LinkedIn")
    if st.button("Aggiungi"):
        if hasattr(st.session_state, 'custom_feed'):
            if st.session_state.custom_feed.add_to_following(new_profile):
                st.success("Profilo aggiunto con successo!")
            else:
                st.error("Errore nell'aggiungere il profilo")
        else:
            st.warning("Effettua prima il login")

# Area principale
st.title("Il tuo Feed Personalizzato")

if hasattr(st.session_state, 'custom_feed'):
    # Bottone per aggiornare il feed
    if st.button("Aggiorna Feed"):
        with st.spinner("Aggiornamento feed in corso..."):
            feed = st.session_state.custom_feed.get_custom_feed()
            st.session_state.custom_feed.save_feed_to_file()
    
    # Carica e mostra il feed salvato
    saved_feed = st.session_state.custom_feed.load_feed_from_file()
    
    if saved_feed:
        st.info(f"Ultimo aggiornamento: {saved_feed.get('last_updated', 'N/A')}")
        
        # Mostra la lista dei profili seguiti
        st.subheader("Profili Seguiti")
        for person in saved_feed.get('following_list', []):
            st.write(f"- {person['name']} (aggiunto il {person['added_on']})")
        
        # Mostra i post
        st.subheader("Post Recenti")
        for post in saved_feed.get('feed', []):
            with st.container():
                st.markdown(f"**{post['author']}**")
                st.write(post['content'])
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"👍 {post['engagement']['likes']}")
                with col2:
                    st.write(f"💬 {post['engagement']['comments']}")
                st.divider()
else:
    st.info("Effettua il login per visualizzare il tuo feed personalizzato")
