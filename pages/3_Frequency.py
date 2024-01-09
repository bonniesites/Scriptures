import streamlit as st
import polars as pl
import nltk
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from streamlit_option_menu import option_menu
import plotly.express as px


st.title("Word Frequency")

options = ["Search", "Table"]
option_select = option_menu(None, options, 
    icons=['search', 'table'], default_index=0, orientation="horizontal")



@st.cache_resource
def download_nltk():
    """ Download NLTK resources """
    nltk.download('punkt')

download_nltk()

scriptures = pl.read_parquet("./data/scriptures.parquet")


st.sidebar.title("Filters")
volume = st.sidebar.selectbox("Volume", 
                              scriptures["volume_title"].unique(maintain_order=True).to_list(), 
                              index=None)
if volume is not None:
    book = st.sidebar.selectbox("Book", 
                                scriptures.filter(pl.col("volume_title") == volume)["book_title"].unique(maintain_order=True).to_list(), 
                                index=None)
else:
    book = None

group_by_mapping = {
    "volume_title": "Volume",
    "book_title": "Book",
    "verse_short_title": "Verse"
}

group_by = st.sidebar.selectbox("Group By", 
                                list(group_by_mapping.keys()), 
                                format_func=lambda x: group_by_mapping[x]
                                )

scriptures = scriptures.filter(
    (volume is None) | (pl.col("volume_title") == volume)
    )\
    .filter(
        (book is None) | (pl.col("book_title") == book)
    )

# st.dataframe(scriptures, hide_index=True, use_container_width=True)

@st.cache_data
def word_frequency(text):
    stop_words = {'ye', 'yea', 'the', 'and', 'of', 'that', 'to', 'in', 'he', 'shall', 'unto', 'for', 'they', 'be', 'is', 'his', 'him', 'not', 'with', 'them', 'it', 'which', 'have', 'a', 'but', 'as', 'i', 'my', 'me', 'thou', 'thy', 'thee', 'was', 'said', 'by', 'are', 'from', 'all', 'their', 'or', 'will', 'upon', 'when', 'had', 'out', 'then', 'there', 'one', 'if', 'we', 'who', 'these', 'your', 'been', 'this', 'an', 'her', 'she', 'were', 'no', 'what', 'also', 'some', 'into', 'more', 'up', 'now', 'do', 'did', 'came'}
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words and w.isalpha()]
    return FreqDist(filtered_sentence)


if option_select == "Search":
    col1, col2 = st.columns([5, 1])
    with col1:
        search = st.text_input("**Search**", 
                               placeholder="Nephi, repentance, cureloms", 
                               help="Separate values by commas", 
                               max_chars=None, 
                               type='default')
    with col2:
        st.markdown("##")
        exact = st.toggle("Exact", value=True, key=None)
    if search != "":
        search = search.split(",")
        search = [s.strip() for s in search]
        search_names = search
        # Exact match
        if exact:
            search = [r"\b" + s + r"\b" for s in search]
        else:
            # Ignore case
            search = ["(?i)" + s for s in search]
        print(search_names)

        results = scriptures\
            .with_columns(
                [pl.col("scripture_text").str.count_matches(search[i]).alias(search_names[i]) for i in range(len(search))]
                )\
            .filter(
                pl.any_horizontal(
                    [pl.col(search_names[i]) > 0 for i in range(len(search_names))]
                )
                )\
            .group_by(group_by)\
            .agg(
                pl.sum(*search_names)
            )\
            .sort(
                search_names[0], descending=True
            )


        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(results, hide_index=True, use_container_width=True)
        with col2:
            fig = px.histogram(results.to_pandas(),
                         y=search_names, 
                         x=group_by, 
                         barmode='group',
                         height=300)
            # Remove top margin
            fig.update_layout(margin=dict(t=0))
            st.plotly_chart(fig, use_container_width=True)
            # st.bar_chart(results, use_container_width=True, x="word", y="frequency", )


if option_select == "Table":
    "### All Words"
    f = open("./data/entire_scriptures.txt", "r")
    entire_scriptures = f.read()
    freq = word_frequency(entire_scriptures)
    freq = pl.DataFrame(freq).transpose(include_header=True, header_name="Word", column_names=["Frequency"])
    st.dataframe(freq, hide_index=True, use_container_width=True)
    "### Top 20 Words"
    fig = px.bar(freq[:20],
                 x="Word", y="Frequency", height=300)
    # Remove top margin
    fig.update_layout(margin=dict(t=0))
    st.plotly_chart(fig, use_container_width=True)
    # st.bar_chart(freq, use_container_width=True, x="word", y="frequency", )






# TODO: It's all backwards. You need to filter/find the words first, then group by the volume, book, chapter, verse, etc.
