import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
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
def scrape_and_index_website(urls):
    """
    Scrapes the provided URLs, extracts the text, and indexes the chunks using FAISS.
    """
    try:
        # Scraping and text chunking
        raw_texts = []
        for url in urls:
            loader = WebBaseLoader(url)
            documents = loader.load()
            raw_text = "\n".join([doc.page_content for doc in documents])
            
            # Split the raw text into chunks
            text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_text(raw_text)
            raw_texts.extend(chunks)

        # Generate embeddings and create a FAISS index
        embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["openai"]["API_KEY"])
        faiss_index = FAISS.from_texts(raw_texts, embeddings)

        return faiss_index
    except Exception as e:
        st.error(f"Error during website scraping or indexing: {e}")
        return None


def ask_groq_with_embeddings(question, faiss_index, groq_api_key, model="llama-3.1-70b-versatile"):
    """
    Sends the user's question and the most relevant context from FAISS to the Groq LLM.
    """
    try:
        # Retrieve top 3 most relevant chunks using FAISS
        relevant_chunks = faiss_index.similarity_search(question, k=3)
        best_context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])

        # Initialize Groq LLM
        llm = ChatGroq(
            temperature=0.2,
            groq_api_key=groq_api_key,
            model_name=model
        )

        # Prompt with context
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

    # Retrieve Groq and OpenAI API keys
    groq_api_key = st.secrets["general"]["GROQ_API_KEY"]

    # Scrape and index website content
    with st.spinner("Scraping and indexing website content..."):
        faiss_index = scrape_and_index_website(urls)

    # User Query Input
    user_query = st.text_input("Ask me a question about Graduate Admissions:", "")
    if st.button("Ask Howie AI"):
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            # Generate an answer based on the most relevant context
            response = ask_groq_with_embeddings(user_query, faiss_index, groq_api_key)

            # Display the conversation
            st.write("---")
            st.markdown(f"**You:** {user_query}")
            st.markdown(f"**Howie AI:** {response}")


if __name__ == "__main__":
    main()
