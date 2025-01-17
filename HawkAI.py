import streamlit as st
from bs4 import BeautifulSoup
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationChain
import os

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
        headers = {"User-Agent": os.environ["USER_AGENT"]}
        
        for url in urls:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                # Extract readable text content (e.g., paragraphs)
                text_content = " ".join(p.get_text() for p in soup.find_all("p"))
                
                # Chunking the text for LLM processing
                text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=500,
                    chunk_overlap=50
                )
                chunks = text_splitter.split_text(text_content)

                # Store chunks for each URL
                url_contexts[url] = chunks
            else:
                st.warning(f"Failed to fetch {url}. HTTP Status: {response.status_code}")

        return url_contexts
    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return {}


def ask_groq(question, contexts, groq_api_key, model="llama-3.1-70b-versatile"):
    """
    Sends the user's question and the most relevant context to the Groq LLM.
    Handles follow-up questions to refine responses.
    """
    try:
        llm = ChatGroq(
            temperature=0.2,
            groq_api_key=groq_api_key,
            model_name=model
        )

        # Select the most relevant context based on keyword matching
        best_context = ""
        for url, chunks in contexts.items():
            combined_context = "\n\n".join(chunks)
            if question.lower() in combined_context.lower():
                best_context = combined_context
                break
        if not best_context:
            best_context = "\n\n".join(contexts.get(list(contexts.keys())[0], []))

        # Prompt template
        prompt = PromptTemplate.from_template("""
        You are Hawk AI, an intelligent assistant representing the University of Hartford Graduate Admissions.
        The following is context scraped from the official website:

        ### CONTEXT ###
        {context}

        The user asked: "{question}"

        If the question is ambiguous or incomplete, ask a follow-up question to clarify. If the context has an answer, provide a concise and accurate response. If the answer is not available in the context, respond with 
        "I'm sorry, I don't have that information. Please visit the website or contact admissions for further assistance."
        """)
        # Execute the prompt
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
