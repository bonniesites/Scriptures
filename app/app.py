import numpy as np
import streamlit as st
import pandas as pd
from streamlit_extras.stoggle import stoggle



scriptures = pd.read_parquet("./data/scriptures.parquet")

if 'show_scripture' not in st.session_state:
    st.session_state.show_scripture = False

if 'show_reference' not in st.session_state:
    st.session_state.show_reference = False

if 'scripture' not in st.session_state:
    st.session_state.scripture = None

def show_scripture():
    st.session_state.show_scripture = True
    st.session_state.show_reference = False

def show_reference():
    st.session_state.show_reference = True

def generate_scripture(volume=None):
    if volume is None or volume == "Any":
        return scriptures.sample()
    else:
        return scriptures[scriptures.volume_title == volume].sample()



st.sidebar.title("Options")
st.sidebar.subheader("Select a volume of scripture")
options = np.append("Any", scriptures.volume_title.unique())
volume = st.sidebar.selectbox("Volume", options)
    


st.title("Random Scripture Generator")
st.subheader("Click the button below to generate a random scripture")




if st.button("Generate", on_click=show_scripture): 
    scripture = generate_scripture(volume)
    st.session_state.scripture = scripture
    st.write(scripture['scripture_text'].values[0])
    stoggle(
    "Show Reference",
    f"{scripture['verse_title'].values[0]}"
    )

# if st.session_state.scripture is not None:
#     st.button("Show reference", on_click=show_reference)

#     if st.session_state.show_reference:
#         st.write(scripture['verse_title'].values[0])
