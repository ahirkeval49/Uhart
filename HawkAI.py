import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from difflib import SequenceMatcher

# Define function to initialize the Groq model
def initialize_groq_model():
    return ChatGroq(
        temperature=0.7,
        model_name="llama-3.1-70b-versatile",
        groq_api_key=st.secrets["general"]["GROQ_API_KEY"]
    )

# Simple text splitting function
def simple_text_split(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Caching-enabled scraping function with timeout
@st.cache_data(show_spinner=True)
def scrape_website(urls):
    headers = {'User-Agent': 'HawkAI/1.0 (+https://www.hartford.edu)'}
    url_contexts = {}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = ' '.join(soup.stripped_strings)
                chunks = simple_text_split(text)
                url_contexts[url] = chunks
            else:
                st.error(f"Failed to retrieve {url}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error scraping {url}: {e}")
    return url_contexts

def find_relevant_chunks(query, contexts, token_limit=6000, prioritized_urls=None):
    """
    Finds the most relevant chunks based on the query, with prioritization for certain URLs
    and ensuring the total token count does not exceed the limit.
    """
    prioritized_urls = prioritized_urls or []  # Default to an empty list if not provided
    relevant_chunks = []
    total_tokens = 0

    # Approximate token count for the query and prompt text
    query_token_count = len(query.split()) + 50  # Reserve 50 tokens for prompt overhead
    available_tokens = token_limit - query_token_count

    # Separate chunks into prioritized and non-prioritized
    prioritized_chunks = []
    other_chunks = []

    for url, chunks in contexts.items():
        for chunk in chunks:
            similarity = SequenceMatcher(None, query, chunk).ratio()
            token_count = len(chunk.split())
            if url in prioritized_urls:
                prioritized_chunks.append((chunk, similarity, token_count))
            else:
                other_chunks.append((chunk, similarity, token_count))

    # Sort chunks by similarity
    prioritized_chunks.sort(key=lambda x: x[1], reverse=True)
    other_chunks.sort(key=lambda x: x[1], reverse=True)

    # Add prioritized chunks first
    for chunk, _, token_count in prioritized_chunks:
        if total_tokens + token_count <= available_tokens:
            relevant_chunks.append(chunk)
            total_tokens += token_count
        else:
            break

    # Add other chunks if space allows
    for chunk, _, token_count in other_chunks:
        if total_tokens + token_count <= available_tokens:
            relevant_chunks.append(chunk)
            total_tokens += token_count
        else:
            break

    return relevant_chunks

def truncate_context_to_token_limit(context, token_limit):
    """
    Truncate the context to fit within the token limit by limiting the number of words.
    Token count is approximated as the word count for simplicity.
    """
    words = context.split()
    truncated_context = " ".join(words[:token_limit])
    return truncated_context

def dynamically_reduce_content(full_prompt, max_tokens=6000):
    """
    Dynamically reduce the content of the full prompt until it's within the token limit.
    Split the context and reduce from the end, as those are likely less relevant.
    """
    parts = full_prompt.split()
    while len(parts) > max_tokens:
        parts = parts[:-1]  # Remove the last word iteratively
    return " ".join(parts)

# Streamlit App
def main():
    st.title("🦅 Hawk AI: Your Admissions Assistant")
    st.write("I am Howie AI, how can I assist you today?")

    # Critical URLs to scrape
    urls = [
        "https://www.hartford.edu/academics/graduate-professional-studies/",
        "https://www.hartford.edu/academics/graduate-professional-studies/about-graduate-and-professional-studies.aspx",
        "https://www.hartford.edu/admission/graduate-admission/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/information-sessions/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-programs.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-student-experience.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/resources.aspx",
        "https://www.hartford.edu/admission/partnerships/default.aspx",
        "https://www.hartford.edu/admission/graduate-admission/financing-grad-education.aspx",
        "https://www.hartford.edu/about/offices-divisions/finance-administration/financial-affairs/bursar-office/tuition-fees/graduate-tuition.aspx",
    ]

    # Automatic scraping on app load
    if 'contexts' not in st.session_state:
        with st.spinner("Scraping data..."):
            st.session_state['contexts'] = scrape_website(urls)

    # Validate contexts
    if 'contexts' not in st.session_state or not st.session_state['contexts']:
        st.error("No contexts available for processing. Scraping might have failed.")
        return

    user_query = st.text_input("Enter your query here:")
    if user_query and st.button("Answer Query"):
        try:
            # Find the most relevant chunks for the user's query
            relevant_chunks = find_relevant_chunks(
                user_query, st.session_state['contexts'], token_limit=6000, prioritized_urls=urls
            )
            context_to_send = "\n\n".join(relevant_chunks)
            context_to_send = truncate_context_to_token_limit(context_to_send, 6000)

            # Initialize Groq model
            groq_model = initialize_groq_model()

            # Generate a response using Groq LLM
            response = groq_model.invoke(
                f"You are Hawk AI, an assistant for University of Hartford Graduate Admissions. Use the following context to answer questions:\n\n{context_to_send}\n\nQuestion: {user_query}",
                timeout=30
            )
            st.markdown(f"**Response:** {response.content.strip()}")
        except Exception as e:
            st.error(f"Error generating response: {e}")

if __name__ == "__main__":
    main()
