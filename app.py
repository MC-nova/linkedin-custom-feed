import streamlit as st
from linkedin_api import Linkedin
import json
from datetime import datetime
import os
from typing import List, Dict

class LinkedInCustomFeed:
    def __init__(self, username: str = None, password: str = None):
        """
        Inizializza il client LinkedIn con le credenziali
        """
        if username and password:
            self.api = Linkedin(username, password)
            self.following_list = []
            self.feed_cache = "feed_cache.json"
        else:
            raise ValueError("Username e password sono richiesti")

    def add_to_following(self, linkedin_url: str) -> bool:
        """
        Aggiunge un profilo alla lista dei seguiti
        """
        try:
            # Estrae l'ID pubblico dall'URL
            public_id = linkedin_url.split('/in/')[-1].strip('/')
            profile = self.api.get_profile(public_id)
            
            if profile:
                self.following_list.append({
                    'public_id': public_id,
                    'name': profile.get('firstName', '') + ' ' + profile.get('lastName', ''),
                    'added_on': datetime.now().isoformat()
                })
                return True
            return False
        except Exception as e:
            st.error(f"Errore nell'aggiunta del profilo: {e}")
            return False

# Inizializzazione dello state se non esiste
if 'custom_feed' not in st.session_state:
    st.session_state.custom_feed = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
        try:
            if email and password:
                st.session_state.custom_feed = LinkedInCustomFeed(email, password)
                st.session_state.logged_in = True
                st.success("Login effettuato con successo!")
            else:
                st.error("Inserisci email e password")
        except Exception as e:
            st.error(f"Errore durante il login: {str(e)}")
    
    # Form per aggiungere nuovi profili (solo se loggato)
    if st.session_state.logged_in:
        st.subheader("Aggiungi Profilo")
        new_profile = st.text_input("URL Profilo LinkedIn")
        if st.button("Aggiungi"):
            if st.session_state.custom_feed.add_to_following(new_profile):
                st.success("Profilo aggiunto con successo!")
            else:
                st.error("Errore nell'aggiungere il profilo")

# Area principale
st.title("Il tuo Feed Personalizzato")

if st.session_state.logged_in and st.session_state.custom_feed:
    try:
        # Bottone per aggiornare il feed
        if st.button("Aggiorna Feed"):
            with st.spinner("Aggiornamento feed in corso..."):
                feed = st.session_state.custom_feed.get_custom_feed()
                st.session_state.custom_feed.save_feed_to_file()
                st.success("Feed aggiornato!")
        
        # Mostra la lista dei profili seguiti
        if st.session_state.custom_feed.following_list:
            st.subheader("Profili Seguiti")
            for person in st.session_state.custom_feed.following_list:
                st.write(f"- {person['name']} (aggiunto il {person['added_on']})")
        else:
            st.info("Non stai ancora seguendo nessun profilo. Aggiungi profili dalla barra laterale.")
            
    except Exception as e:
        st.error(f"Si è verificato un errore: {str(e)}")
else:
    st.info("Effettua il login per visualizzare il tuo feed personalizzato")
