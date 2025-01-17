import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import TextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
import re
from difflib import SequenceMatcher

# Config & Styling
st.set_page_config(page_title="Hawk AI", page_icon="🦅", layout="centered")
st.markdown("""
<style>
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
os.environ["USER_AGENT"] = "HawkAI/1.0 (+https://www.hartford.edu)"

# Helper Functions
def scrape_website(urls):
    url_contexts = {}
    for url in urls:
        try:
            loader = WebBaseLoader(url, user_agent=os.getenv("USER_AGENT"))
            documents = loader.load()
            text_splitter = TextSplitter(chunk_size=500, overlap_size=100)
            chunks = text_splitter.split("\n".join([doc.text for doc in documents]))
            url_contexts[url] = chunks
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")
    return url_contexts

def preprocess_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def find_relevant_chunks(question, contexts, threshold=0.3):
    question = preprocess_text(question)
    relevant_chunks = []
    for url, chunks in contexts.items():
        for chunk in chunks:
            if SequenceMatcher(None, question, preprocess_text(chunk)).ratio() > threshold:
                relevant_chunks.append(chunk)
    return sorted(relevant_chunks, key=lambda x: SequenceMatcher(None, question, preprocess_text(x)).ratio(), reverse=True)[:3]

def ask_groq(question, contexts, groq_api_key):
    try:
        llm = ChatGroq(temperature=0.2, groq_api_key=groq_api_key)
        relevant_chunks = find_relevant_chunks(question, contexts)
        best_context = "\n\n".join(relevant_chunks)
        prompt = PromptTemplate("You are Hawk AI, an intelligent assistant for the University of Hartford Graduate Admissions. Here's the context: {context} The user asked: '{question}' Please provide a concise and accurate response.")
        response = llm.invoke(prompt.format(context=best_context, question=question))
        return response.content.strip() if response.content else "No information available."
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Error in response generation."

# Main Application
def main():
    st.title("🦅 Hawk AI: Your Admissions Assistant")
    st.write("How can I assist you today?")
    urls = [ # List of URLs
        "https://www.hartford.edu/admission/graduate-admission/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/",
        # Add other relevant URLs
    ]
    groq_api_key = st.secrets["GROQ_API_KEY"]
    contexts = scrape_website(urls)
    user_query = st.text_input("Ask me a question about Graduate Admissions:")
    if st.button("Ask Howie AI"):
        response = ask_groq(user_query, contexts, groq_api_key)
        st.write(f"**Howie AI:** {response}")

if __name__ == "__main__":
    main()
