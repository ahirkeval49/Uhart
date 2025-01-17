import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from difflib import SequenceMatcher

# Define function to initialize the Groq model
def initialize_groq_model():
    return ChatGroq(
        temperature=0.2,
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

# Function to find relevant chunks based on user query
def find_relevant_chunks(query, contexts, token_limit=1000):
    relevant_chunks = []
    total_tokens = 0
    
   # Approximate token count for the query and prompt text
    query_token_count = len(query.split()) + 50  # Extra 50 tokens for prompt text
    available_tokens = token_limit - query_token_count
    
    for url, chunks in contexts.items():
        for chunk in chunks:
            similarity = SequenceMatcher(None, query, chunk).ratio()
            token_count = len(chunk.split())  # Approximate token count by word count
            relevant_chunks.append((chunk, similarity, token_count))

    # Sort chunks by similarity
    relevant_chunks = sorted(relevant_chunks, key=lambda x: x[1], reverse=True)

    # Dynamically add chunks until token limit is reached
    selected_chunks = []
    for chunk, _, token_count in relevant_chunks:
        if total_tokens + token_count <= token_limit:
            selected_chunks.append(chunk)
            total_tokens += token_count
        else:
            break

    return selected_chunks
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
    if user_query:
        if st.button("Answer Query"):
            prioritized_urls = [
                "https://www.hartford.edu/academics/graduate-professional-studies/",
                "https://www.hartford.edu/academics/graduate-professional-studies/about-graduate-and-professional-studies.aspx",
                "https://www.hartford.edu/admission/graduate-admission/default.aspx",
                "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/information-sessions/default.aspx",
                "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-programs.aspx",
                "https://www.hartford.edu/academics/graduate-professional-studies/graduate-student-experience.aspx",
                "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/resources.aspx",
                "https://www.hartford.edu/admission/partnerships/default.aspx",
                "https://www.hartford.edu/admission/graduate-admission/financing-grad-education.aspx",
                "https://www.hartford.edu/about/offices-divisions/finance-administration/financial-affairs/bursar-office/tuition-fees/graduate-tuition.aspx",
            ]

            # Debugging: Ensure inputs to find_relevant_chunks are valid
            if not isinstance(user_query, str):
                st.error("Query must be a string.")
                return
            if not isinstance(st.session_state['contexts'], dict):
                st.error("Contexts must be a dictionary.")
                return
            if not isinstance(prioritized_urls, list):
                st.error("Prioritized URLs must be a list.")
                return

            try:
                # Find the most relevant chunks for the user's query
                relevant_chunks = find_relevant_chunks(
                    user_query, st.session_state['contexts'], token_limit=6000, prioritized_urls=prioritized_urls
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
