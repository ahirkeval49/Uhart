import streamlit as st
import requests
from bs4 import BeautifulSoup

# Simple text splitting function
def simple_text_split(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Scraping function with a custom user agent
def scrape_website(urls):
    headers = {'User-Agent': 'HawkAI/1.0 (+https://www.hartford.edu)'}
    url_contexts = {}
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = ' '.join(soup.stripped_strings)  # Clean text by removing extra whitespace
                chunks = simple_text_split(text)
                url_contexts[url] = chunks
            else:
                st.error(f"Failed to retrieve {url}: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")
    return url_contexts

# Streamlit App
def main():
    st.title("🦅 Hawk AI: Your Admissions Assistant")
    st.write("Ask me any questions about Graduate Admissions at the University of Hartford.")

    urls = [
        "https://www.hartford.edu/admission/graduate-admission/default.aspx",
        "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/",
        # Add more URLs as needed
    ]

    # Automatic scraping on app load
    contexts = scrape_website(urls)
    st.session_state['contexts'] = contexts  # Store contexts in session state if needed for re-use

    user_query = st.text_input("Enter your query here:")
    if user_query:
        if st.button("Answer Query"):
            # Placeholder response generation
            response = "Placeholder response based on user query and scraped content."
            st.markdown(f"**Response:** {response}")
        else:
            st.info("Enter a query and click the button to get a response.")

if __name__ == "__main__":
    main()
