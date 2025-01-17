import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import TextSplitter

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
                text_splitter = TextSplitter(chunk_size=500, overlap_size=100)
                chunks = text_splitter.split(text)
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
    
    if st.button("Scrape Websites"):
        with st.spinner("Fetching content..."):
            contexts = scrape_website(urls)
            st.success("Content fetched successfully!")

    user_query = st.text_input("Enter your query here:")
    if st.button("Answer Query"):
        if user_query:
            # Assuming a simple response function is defined
            # You would need to implement or specify how the response is generated based on the context
            response = "Placeholder response based on user query and scraped content."
            st.markdown(f"**Response:** {response}")
        else:
            st.warning("Please enter a query to get a response.")

if __name__ == "__main__":
    main()
