import streamlit as st
import requests

# Streamlit UI
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
st.title("📢 News Summarization & Sentiment Analysis")

# User Input: Company Name
company_name = st.text_input("Enter a company name:", "")

# Fetch news when button is clicked
if st.button("Get News Analysis"):
    if company_name:
        api_url = f"http://127.0.0.1:8000/get_news?company={company_name}"
        
        # Call FastAPI backend
        response = requests.get(api_url)
        print("🔍 API Response:", response.text)  # Debugging Log

        if response.status_code == 200:
            news_data = response.json()

            if "error" in news_data:
                st.error("⚠ No news found. Try another company.")
            else:
                st.subheader(f"📰 News for {company_name}")
                
                # Display articles
                for article in news_data["Articles"]:
                    st.markdown(f"### [{article['Title']}]({article['URL']}) - {article['Source']}")
                    st.write(f"📅 Published at: {article['Published At']}")
                    st.write(f"**Summary:** {article['Summary']}")
                    st.write(f"**Sentiment:** {article['Sentiment']}")
                    st.write(f"**Topics:** {', '.join(article['Topics']) if article['Topics'] else 'N/A'}")
                    st.write("---")

                # Display Comparative Sentiment Analysis
                st.subheader("📊 Comparative Sentiment Analysis")
                st.json(news_data["Comparative Sentiment Score"])

        else:
            st.error("⚠ Error fetching data from API. Try again.")
    else:
        st.warning("Please enter a company name.")
