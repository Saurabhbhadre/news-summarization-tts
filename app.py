import streamlit as st
import requests

# Streamlit UI
st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
st.title("📢 News Summarization & Sentiment Analysis")

# User Input: Company Name
company_name = st.text_input("Enter a company name:", "")

# Hugging Face API URLs
API_BASE_URL = "https://saurabhbhadre-news-summarization-api.hf.space/get_news"
TTS_API_URL = "https://saurabhbhadre-news-summarization-api.hf.space/generate_tts"

# Fetch news when button is clicked
if st.button("Get News Analysis"):
    if company_name:
        api_url = f"{API_BASE_URL}?company={company_name}"
        
        try:
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                news_data = response.json()

                if "error" in news_data:
                    st.error("⚠ No news found. Try another company.")
                else:
                    st.subheader(f"📰 News for {company_name}")
                    
                    summary_text = ""
                    for article in news_data.get("Articles", []):
                        st.markdown(f"### [{article['Title']}]({article['URL']}) - {article['Source']}")
                        st.write(f"📅 Published at: {article['Published At']}")
                        st.write(f"**Summary:** {article['Summary']}")
                        st.write(f"**Sentiment:** {article['Sentiment']}")
                        st.write(f"**Topics:** {', '.join(article['Topics']) if article['Topics'] else 'N/A'}")
                        st.write("---")

                        summary_text += article["Summary"] + " "

                    # Display Comparative Sentiment Analysis
                    if "Comparative Sentiment Score" in news_data:
                        st.subheader("📊 Comparative Sentiment Analysis")
                        st.json(news_data["Comparative Sentiment Score"])
                    else:
                        st.warning("⚠ No comparative sentiment data available.")

                    # Generate and Play TTS Audio in Hindi
                    if summary_text:
                        tts_response = requests.post(TTS_API_URL, json={"text": summary_text})

                        if tts_response.status_code == 200:
                            tts_data = tts_response.json()

                            if "error" in tts_data:
                                st.error(f"⚠ TTS Error: {tts_data['error']}")
                            else:
                                audio_url = "https://saurabhbhadre-news-summarization-api.hf.space/download_tts"
                                st.audio(audio_url, format="audio/mp3")
                        else:
                            st.error("⚠ Error fetching TTS audio.")

            else:
                st.error(f"⚠ Error fetching data from API. Status Code: {response.status_code}")
                st.text(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"⚠ API request failed: {e}")

    else:
        st.warning("Please enter a company name.")
