import streamlit as st
from bs4 import BeautifulSoup
import requests
import PyPDF2
from langchain import LangChain
from io import BytesIO

# Initialize LangChain
lc = LangChain(model="llama-3.1-70b-versatile", api_key=st.secrets["general"]["GROQ_API_KEY"])

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

# Scraping function
def scrape_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([p.text for p in soup.find_all('p')])
    else:
        return "Failed to fetch data."

# Main app function
def main():
    st.title("Hawk AI: Graduate Admissions Assistant")
    st.write("I am Howie AI, how can I assist you today?")

    # Concatenate texts from all URLs
    all_texts = [scrape_text(url) for url in urls]

    # User query input
    user_query = st.text_input("Please enter your query related to Graduate Admissions:")
    
    if user_query:
        response = lc.ask(user_query, context=all_texts)
        st.write("Howie AI:", response)
    else:
        st.write("Please enter a question to get help from Howie AI.")

if __name__ == "__main__":
    main()
