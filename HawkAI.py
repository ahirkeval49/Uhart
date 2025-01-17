import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
import re
from difflib import SequenceMatcher

########################################
# STREAMLIT CONFIG & STYLING
########################################

st.set_page_config(page_title="Hawk AI", page_icon="🦅", layout="centered")

# Hide Streamlit footer
HIDE_FOOTER = """
<style>
footer {visibility: hidden;}
</style>
"""
st.markdown(HIDE_FOOTER, unsafe_allow_html=True)

# Set USER_AGENT environment variable for web scraping
os.environ["USER_AGENT"] = "HawkAI/1.0 (+https://www.hartford.edu)"

########################################
# HELPER FUNCTIONS
########################################

@st.cache_data(show_spinner=True)
def scrape_website(urls):
    """
    Scrapes the provided URLs, extracts the text, and splits it into manageable chunks.
    """
    try:
        url_contexts = {}
        for url in urls:
            # Load website content
            loader = WebBaseLoader(url)
            documents = loader.load()
            raw_text = "\n".join([doc.page_content for doc in documents])

            # Chunking the text for LLM processing
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # Use smaller chunks for better context
                chunk_overlap=100  # Avoid overlap issues
            )
            chunks = text_splitter.split_text(raw_text)

            # Log chunk sizes for debugging
            for idx, chunk in enumerate(chunks):
                if len(chunk) > 500:
                    print(f"Chunk {idx + 1} exceeds size limit: {len(chunk)}")

            # Store chunks for each URL
            url_contexts[url] = chunks

        return url_contexts
    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return {}


def preprocess_text(text):
    """
    Preprocess text by removing punctuation and converting to lowercase.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text


def find_relevant_chunks(question, contexts, threshold=0.3, top_n=3):
    """
    Finds the most relevant chunks based on fuzzy matching and keyword overlap.
    """
    question = preprocess_text(question)
    relevant_chunks = []

    for url, chunks in contexts.items():
        for chunk in chunks:
            chunk_preprocessed = preprocess_text(chunk)
            similarity = SequenceMatcher(None, question, chunk_preprocessed).ratio()
            if similarity >= threshold:
                relevant_chunks.append((chunk, similarity))

    # Sort by similarity score
    relevant_chunks = sorted(relevant_chunks, key=lambda x: x[1], reverse=True)

    # Return the top N chunks
    return [chunk[0] for chunk in relevant_chunks[:top_n]]


def ask_groq(question, contexts, groq_api_key, model="llama-3.1-70b-versatile"):
    """
    Sends the user's question and the most relevant context to the Groq LLM.
    """
    try:
        llm = ChatGroq(
            temperature=0.2,
            groq_api_key=groq_api_key,
            model_name=model
        )

        # Find the most relevant chunks
        relevant_chunks = find_relevant_chunks(question, contexts)
        best_context = "\n\n".join(relevant_chunks)

        # Debugging: Log context matching process
        if st.sidebar.checkbox("Show debug info"):
            st.sidebar.write("Matched Chunks:")
            st.sidebar.write(relevant_chunks)

        # If no relevant chunks are found, fallback response
        if not best_context.strip():
            return (
                "I'm sorry, I couldn't find specific information for your query. "
                "Please visit the University of Hartford website or contact admissions for further assistance."
            )

        # Prompt template
        prompt = PromptTemplate.from_template("""
        You are Hawk AI, an intelligent assistant representing the University of Hartford Graduate Admissions.
        The following is context scraped from the official website:

        ### CONTEXT ###
        {context}

        The user asked: "{question}"

        Provide a concise and accurate response. If the answer is not available in the context, respond with 
        "I'm sorry, I don't have that information. Please visit the website or contact admissions for further assistance."
        """)
        response = llm.invoke(prompt.format_prompt(context=best_context, question=question).to_string())
        return response.content.strip()

    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I'm sorry, I encountered an issue. Please try again later."


########################################
# MAIN APP
########################################

def main():
    # Greet the user
    st.title("🦅 Hawk AI: Your Admissions Assistant")
    st.write("I am Howie AI, how can I assist you today?")

    # URLs for scraping
    urls = [
        "https://www.hartford.edu/admission/graduate-admission/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-programs.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/information-sessions/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-student-experience.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/resources.aspx",
        "https://www.hartford.edu/admission/partnerships/default.aspx",
        "https://www.hartford.edu/admission/graduate-admission/Frequently%20Asked%20Questions.aspx",
        "https://www.hartford.edu/about/offices-divisions/finance-administration/financial-affairs/bursar-office/tuition-fees/graduate-tuition.aspx"
    ]

    # Retrieve Groq API key
    groq_api_key = st.secrets["general"]["GROQ_API_KEY"]

    # Cache and scrape website content
    with st.spinner("Scraping website content..."):
        contexts = scrape_website(urls)

    # User Query Input
    user_query = st.text_input("Ask me a question about Graduate Admissions:", "")
    if st.button("Ask Howie AI"):
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            # Generate an answer based on the most relevant context
            response = ask_groq(user_query, contexts, groq_api_key)

            # Display the conversation
            st.write("---")
            st.markdown(f"**You:** {user_query}")
            st.markdown(f"**Howie AI:** {response}")


if __name__ == "__main__":
    main()
