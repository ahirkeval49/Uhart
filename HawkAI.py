import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq  # Correct import for Groq integration
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
    st.write("I am Howie AI, how can I assist you today?")
# Define URLs to scrape
urls = [
    "https://www.hartford.edu/academics/graduate-professional-studies/",
    "https://www.hartford.edu/academics/graduate-professional-studies/about-graduate-and-professional-studies.aspx",
    "https://www.hartford.edu/admission/graduate-admission/default.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/information-sessions/default.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-programs.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/graduate-student-experience.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/graduate-studies/resources.aspx",
    "https://www.hartford.edu/admission/partnerships/default.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/partnerships.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/programs/default.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-architecture/master-of-architecture.aspx",
    "https://www.hartford.edu/barney/academics/business-administration/dual-mba-march.aspx",
    "https://www.hartford.edu/academics/schools-colleges/art/academics/graduate/illustration.aspx",
    "https://www.hartford.edu/academics/schools-colleges/art/academics/graduate/photography.aspx",
    "https://www.hartford.edu/barney/academics/management-marketing-and-entrepreneurship/mba.aspx",
    "https://www.hartford.edu/barney/academics/accounting-and-taxation/masters-in-accounting-and-taxation.aspx",
    "https://www.hartford.edu/barney/academics/business-administration/msba.aspx",
    "https://www.hartford.edu/barney/academics/business-administration/dual-msat-mba.aspx",
    "https://www.hartford.edu/barney/academics/business-administration/mba-certificates.aspx",
    "https://www.hartford.edu/barney/academics/business-administration/dual-m-eng-mba.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/psychology/dual-msop-mba.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/communication/ma-in-integrated-communication.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/computing-sciences/ms-computer-science.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/med-in-early-childhood-elementary.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/med-elementary.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/montessori-education/med-in-education-montessori-concentration.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/med-in-special-education.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/edd-in-educational-leadership.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-education/certificate-college-teaching.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-civil-environmental-and-biomedical-engineering/meng-in-civil-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-electrical-and-computer-engineering/meng-in-electrical-and-computer-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-mechanical-aerospace-and-acoustical-engineering/meng-in-mechanical-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-civil-environmental-and-biomedical-engineering/ms-in-civil-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-electrical-and-computer-engineering/ms-in-electrical-and-computer-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/department-of-mechanical-aerospace-and-acoustical-engineering/ms-in-mechanical-engineering.aspx",
    "https://www.hartford.edu/academics/schools-colleges/ceta/academics/professional-certificates.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-nursing/msn-in-nursing.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-nursing/dnp-nursing.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-rehabilitation-sciences/ms-in-occupational-therapy.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-rehabilitation-sciences/doctor-of-physical-therapy.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-rehabilitation-sciences/physical-therapy-orthopedic-residency.aspx",
    "https://www.hartford.edu/academics/graduate-professional-studies/programs/post-baccalaureate-premedical-certificate.aspx",
    "https://www.hartford.edu/academics/schools-colleges/enhp/academics/department-of-rehabilitation-sciences/ms-in-prosthetics-and-orthotics.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/psychology/accelerated-ba-ms-in-organizational-psychology.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/psychology/ms-in-organizational-psychology.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/psychology/ms-and-6th-Year-certificate-school-psychology.aspx",
    "https://www.hartford.edu/academics/schools-colleges/arts-sciences/academics/departments-and-centers/psychology/psyd-clinical-psychology/default.aspx",
    "https://www.hartford.edu/admission/graduate-admission/financing-grad-education.aspx",
    "https://www.hartford.edu/about/offices-divisions/finance-administration/financial-affairs/bursar-office/tuition-fees/graduate-tuition.aspx"
]
    # Automatic scraping on app load
    if 'contexts' not in st.session_state:
        st.session_state['contexts'] = scrape_website(urls)

    user_query = st.text_input("Enter your query here:")
    if user_query:
        if st.button("Answer Query"):
            # Collect all text chunks
            all_text = ' '.join([chunk for url_chunks in st.session_state['contexts'].values() for chunk in url_chunks])

            # Initialize Groq model
            groq_model = initialize_groq_model()

            # Generate a response using Groq LLM
            try:
                response = groq_model.invoke(
                    f"You are Hawk AI, an assistant for University of Hartford Graduate Admissions. Use the following context to answer questions:\n\n{all_text}\n\nQuestion: {user_query}"
                )
                st.markdown(f"**Response:** {response.content.strip()}")
            except Exception as e:
                st.error(f"Error generating response: {e}")


if __name__ == "__main__":
    main()
