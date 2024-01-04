import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from streamlit_option_menu import option_menu
import plotly.express as px

scriptures = pl.read_parquet("./data/scriptures.parquet")

volumes = ['Old Testament', 'New Testament', 'Book of Mormon', 'Doctrine and Covenants', 'Pearl of Great Price']

st.sidebar.title("Filters")
volume = st.sidebar.selectbox("Volume", volumes, index=None)

st.title("Word Frequency")

@st.cache_data
def word_frequency(text):
    stop_words = {'ye', 'yea', 'the', 'and', 'of', 'that', 'to', 'in', 'he', 'shall', 'unto', 'for', 'they', 'be', 'is', 'his', 'him', 'not', 'with', 'them', 'it', 'which', 'have', 'a', 'but', 'as', 'i', 'my', 'me', 'thou', 'thy', 'thee', 'was', 'said', 'by', 'are', 'from', 'all', 'their', 'or', 'will', 'upon', 'when', 'had', 'out', 'then', 'there', 'one', 'if', 'we', 'who', 'these', 'your', 'been', 'this', 'an', 'her', 'she', 'him', 'had', 'were', 'no', 'what', 'also', 'some', 'into', 'more', 'up', 'now', 'do', 'did', 'came'}
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words and w.isalpha()]
    return FreqDist(filtered_sentence)

scriptures = scriptures.filter(
    (volume == None) |
    (pl.col("volume_title") == volume)
    ).select(
        pl.col("scripture_text").str.concat(" ")
    ).item()
freq = pl.DataFrame(word_frequency(scriptures)).transpose(include_header=True, header_name="Word", column_names=["Frequency"])

# st.dataframe(freq, hide_index=True)
# scriptures[:1001]
    
options = ["Search", "Table"]
option_select = option_menu(None, options, 
    icons=['search', 'table'], default_index=0, orientation="horizontal")


if option_select == "Search":
    col1, col2 = st.columns([5, 1])
    with col1:
        search = st.text_input("**Search**", placeholder="Nephi, Sword, Arm", help="Separate values by commas", max_chars=None, type='default')
    with col2:
        st.markdown("##")
        exact = st.toggle("Exact", value=False, key=None)
    if search != "":
        search = search.split(",")
        search = [s.strip() for s in search]

        # Exact match
        if exact:
            search = ["^" + s + "$" for s in search]
        else:
            # Ignore case
            search = ["(?i)" + s for s in search]

            
        search = "|".join(search)
        print(search)
        results = freq.filter(pl.col("Word").str.contains(search))

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(results, hide_index=True, use_container_width=True)
        with col2:
            fig = px.bar(results, x="Word", y="Frequency", height=300)
            # Remove top margin
            fig.update_layout(margin=dict(t=0))
            st.plotly_chart(fig, use_container_width=True)
            # st.bar_chart(results, use_container_width=True, x="word", y="frequency", )


if option_select == "Table":
    st.dataframe(freq, hide_index=True, use_container_width=True)
    fig = px.bar(freq[:20],
                 x="Word", y="Frequency", height=300)
    # Remove top margin
    fig.update_layout(margin=dict(t=0))
    st.plotly_chart(fig, use_container_width=True)
    # st.bar_chart(freq, use_container_width=True, x="word", y="frequency", )