import streamlit as st
import polars as pl
import spacy
from spacy.tokens import DocBin

# Disclaimer
n = st.sidebar.number_input("Number of verses", min_value=1, max_value=100, value=5, step=1, format="%d")

st.title("Similar Verses")

@st.cache_resource
def read_docs():
    """ Read in the docs """
    model_name = 'en_core_web_md'
    # if not spacy.util.is_package(model_name):
    #     print(f"Downloading model '{model_name}'")
    #     spacy.cli.download(model_name)
    #     print(f"Finished downloading model '{model_name}'")

    bytes_data = open("scriptures2.spacy", "rb").read()
    nlp = spacy.load(model_name)
    doc_bin = DocBin().from_bytes(bytes_data)
    docs = list(doc_bin.get_docs(nlp.vocab))
    return docs

docs = read_docs()

def most_similar(search_verse, verses, n):
    similarities = [search_verse.similarity(doc) for doc in verses]
    return sorted(enumerate(similarities), key=lambda item: -item[1])[:n]

# Read in scriptures
scriptures = pl.read_parquet("./data/scriptures.parquet").with_row_index()
verses = scriptures["verse_title"].unique(maintain_order=True).to_list()

search_verse = st.selectbox("Search Verse", placeholder="ex. John 3:16", options=verses, index=None)

if search_verse is not None:
    search_verse_index = verses.index(search_verse)
    search_doc = docs[search_verse_index]
    # search_doc.text 
    related = most_similar(search_doc, docs, n)
    related = pl.DataFrame(related, 
                           schema={"verse": pl.UInt32, "similarity": pl.Float64},
                           orient="row"
                           )
    
    scriptures = scriptures.join(
        related, 
        left_on="index", 
        right_on="verse"
        )\
        .sort(
            by="similarity", 
            descending=True
            )\
        .select('verse_title', "scripture_text")\
        .to_dict(as_series=False)
    st.write(">" + scriptures["scripture_text"][0])
    # scriptures
    st.write("---")
    st.write("##### Most similar verses:")
    for i in range(1, n):
            st.write(scriptures["verse_title"][i])
            st.write(">" + scriptures["scripture_text"][i])
            st.write("---")

    # st.dataframe(scriptures)