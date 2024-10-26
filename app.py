import streamlit as st
from linkedin_api import Linkedin
from datetime import datetime, timedelta
import pandas as pd

class LinkedInFeedManager:
    def __init__(self, email: str, password: str):
        """
        Inizializza il client LinkedIn usando l'API non ufficiale
        """
        self.api = Linkedin(email, password)
        # Usa st.session_state invece del file locale
        if 'following_list' not in st.session_state:
            st.session_state.following_list = []
    
    def add_profile(self, profile_url: str) -> bool:
        """
        Aggiunge un profilo alla lista dei seguiti
        """
        try:
            # Estrae l'ID del profilo dall'URL
            profile_id = profile_url.split('/in/')[-1].strip('/')
            
            # Verifica se il profilo esiste e ottiene le informazioni
            profile_info = self.api.get_profile(profile_id)
            
            if profile_info:
                # Aggiungi alla lista se non è già presente
                if not any(p['id'] == profile_id for p in st.session_state.following_list):
                    st.session_state.following_list.append({
                        'id': profile_id,
                        'name': f"{profile_info.get('firstName', '')} {profile_info.get('lastName', '')}",
                        'headline': profile_info.get('headline', ''),
                        'added_on': datetime.now().isoformat()
                    })
                    return True
            return False
        except Exception as e:
            st.error(f"Errore nell'aggiunta del profilo: {str(e)}")
            return False
    
    def get_posts(self, days_back: int = 7) -> list:
        """
        Recupera i post recenti dai profili seguiti
        """
        all_posts = []
        cut_off_date = datetime.now() - timedelta(days=days_back)
        
        for profile in st.session_state.following_list:
            try:
                # Recupera i post del profilo
                posts = self.api.get_profile_posts(profile['id'], limit=10)
                
                for post in posts:
                    post_date = datetime.fromtimestamp(post.get('time', 0)/1000)
                    if post_date >= cut_off_date:
                        all_posts.append({
                            'author': profile['name'],
                            'date': post_date.strftime('%Y-%m-%d %H:%M'),
                            'text': post.get('commentary', ''),
                            'likes': post.get('numLikes', 0),
                            'comments': post.get('numComments', 0)
                        })
            except Exception as e:
                st.warning(f"Impossibile recuperare i post per {profile['name']}: {str(e)}")
                continue
        
        # Ordina i post per data
        return sorted(all_posts, key=lambda x: x['date'], reverse=True)

# Configurazione Streamlit
st.set_page_config(page_title="LinkedIn Custom Feed", page_icon="📱", layout="wide")

# Configurazione tema personalizzato
st.markdown("""
    <style>
    .stButton>button {
        background-color: #0A66C2;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #f3f2ef;
    }
    </style>
    """, unsafe_allow_html=True)

# Gestione dello stato della sessione
if 'feed_manager' not in st.session_state:
    st.session_state.feed_manager = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Sidebar per login e gestione profili
with st.sidebar:
    st.title("📱 LinkedIn Custom Feed")
    
    if not st.session_state.logged_in:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email LinkedIn")
            password = st.text_input("Password LinkedIn", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                try:
                    st.session_state.feed_manager = LinkedInFeedManager(email, password)
                    st.session_state.logged_in = True
                    st.success("Login effettuato con successo!")
                except Exception as e:
                    st.error(f"Errore durante il login: {str(e)}")
    
    if st.session_state.logged_in:
        st.subheader("Aggiungi Profilo")
        with st.form("add_profile_form"):
            profile_url = st.text_input("URL Profilo LinkedIn", 
                                      placeholder="https://www.linkedin.com/in/username")
            submit_profile = st.form_submit_button("Aggiungi Profilo")
            
            if submit_profile:
                if st.session_state.feed_manager.add_profile(profile_url):
                    st.success("Profilo aggiunto con successo!")
                else:
                    st.error("Errore nell'aggiungere il profilo")

# Area principale
st.title("Il tuo Feed Personalizzato")

if st.session_state.logged_in:
    # Filtro temporale
    col1, col2 = st.columns([2, 1])
    with col1:
        days = st.slider("Mostra post degli ultimi giorni:", 1, 30, 7)
    with col2:
        refresh = st.button("🔄 Aggiorna Feed", use_container_width=True)
    
    # Recupera e mostra i post
    if refresh:
        with st.spinner("Recupero i post..."):
            posts = st.session_state.feed_manager.get_posts(days)
            
            if posts:
                # Converti in DataFrame per una migliore visualizzazione
                df = pd.DataFrame(posts)
                
                # Mostra ogni post in un container
                for _, post in df.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd;'>
                            <h3 style='margin: 0; color: #0A66C2;'>{post['author']}</h3>
                            <p style='color: #666; font-size: 0.8em;'>{post['date']}</p>
                            <p style='margin: 10px 0;'>{post['text']}</p>
                            <div style='display: flex; gap: 20px;'>
                                <span>👍 {post['likes']}</span>
                                <span>💬 {post['comments']}</span>
                            </div>
                        </div>
                        <br>
                        """, unsafe_allow_html=True)
            else:
                st.info("Nessun post trovato nel periodo selezionato")
    
    # Mostra profili seguiti
    with st.sidebar:
        st.subheader("Profili Seguiti")
        if len(st.session_state.following_list) > 0:
            for profile in st.session_state.following_list:
                st.markdown(f"""
                <div style='background-color: white; padding: 10px; border-radius: 5px; margin: 5px 0; border: 1px solid #ddd;'>
                    <strong>{profile['name']}</strong><br>
                    <small>{profile.get('headline', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Non stai seguendo ancora nessun profilo")
else:
    st.info("Effettua il login per visualizzare il tuo feed personalizzato")
