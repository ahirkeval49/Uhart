import streamlit as st
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
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
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_text(raw_text)

            # Store chunks for each URL
            url_contexts[url] = chunks

        return url_contexts
    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return {}


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

        Provide a concise and accurate response. If the answer is not available in the context, respond with 
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
    ]

    st.sidebar.info("Scraping content from these URLs:")
    for url in urls:
        st.sidebar.write(f"- [{url}]({url})")

    # Retrieve Groq API key
    groq_api_key = st.secrets["general"]["GROQ_API_KEY"]

    # Cache and scrape website content
    with st.spinner("Scraping website content..."):
        contexts = scrape_website(urls)

    # FAQ Section
    st.sidebar.header("Frequently Asked Questions")
    faqs = {
        "How can I apply?": "You can apply directly through the Graduate Admissions portal on the University of Hartford's website.",
        "What are the admission requirements?": "Admissions requirements vary by program. Typically, you'll need transcripts, letters of recommendation, and a personal statement.",
        "What is the application fee?": "The application fee for graduate programs is typically $50.",
        "When are application deadlines?": "Deadlines vary by program. Please refer to the program-specific page on the website."
    }

    for question, answer in faqs.items():
        st.sidebar.markdown(f"**{question}**")
        st.sidebar.write(answer)

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
