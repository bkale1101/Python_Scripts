import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import speech_recognition as sr
from langdetect import detect, DetectorFactory
import re
from spellchecker import SpellChecker
import requests
from bs4 import BeautifulSoup

DetectorFactory.seed = 0

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def correct_spelling(text):
    spell = SpellChecker()
    corrected_words = []
    for word in text.split():
        corrected_word = spell.correction(word)
        if corrected_word is not None:
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    return ' '.join(corrected_words)

def detect_sentiment(input_text):
    try:
        if not input_text.strip():
            return "Please enter a paragraph.", "", {}, 0, 0

        if detect(input_text) != 'en':
            return "Please provide text in English.", "", {}, 0, 0

        input_text = preprocess_text(input_text)
        input_text = correct_spelling(input_text)

        sid_obj = SentimentIntensityAnalyzer()
        sentiment_scores = sid_obj.polarity_scores(input_text)
        word_sentiments = {}
        positive_words = []
        negative_words = []

        for word in input_text.split():
            word_sentiment = sid_obj.polarity_scores(word)['compound']
            word_sentiments[word] = word_sentiment
            if word_sentiment > 0:
                positive_words.append(word)
            elif word_sentiment < 0:
                negative_words.append(word)

        total_words = len(positive_words) + len(negative_words)
        if total_words == 0:
            return ("Can't provide text sentiment due to the following reasons:\n"
                    "1. Check if the text is in English.\n"
                    "2. Check the spellings of words for more accurate results."), "", {}, 0, 0

        positive_percentage = len(positive_words) / total_words * 100
        negative_percentage = len(negative_words) / total_words * 100

        compound_score = sentiment_scores['compound']
        if compound_score >= 0.05:
            overall_sentiment = 'Positive'
            sentiment_emoji = '😊'
        elif compound_score <= -0.05:
            overall_sentiment = 'Negative'
            sentiment_emoji = '😞'
        else:
            overall_sentiment = 'Neutral'
            sentiment_emoji = '😐'

        num_positive_words = len(positive_words)
        num_negative_words = len(negative_words)

        response_message = (f"<div style='padding: 10px; border-radius: 10px; background-color: "
                            f"{'lightgreen' if overall_sentiment.lower() == 'positive' else 'lightcoral'};'>"
                            f"<span style='color: {'darkgreen' if overall_sentiment.lower() == 'positive' else 'darkred'};'>"
                            f"Based on the analysis of your input, the overall suggested paragraph/sentence is "
                            f"{overall_sentiment.lower()}.</span></div>\n\n")
        st.write(f"Sentiment Emotion: {sentiment_emoji}")
        response_message += "Percentage breakdown:\n"
        response_message += f"- Positive: {positive_percentage:.2f}%\n"
        response_message += f"- Negative: {negative_percentage:.2f}%\n\n"
        response_message += "Here is your input:\n\n"
        for word in input_text.split():
            if word in positive_words:
                response_message += f"<span style='background-color:#2AAA8A; padding: 2px 5px; border-radius: 5px;'>{word}</span> "
            elif word in negative_words:
                response_message += f"<span style='background-color:#FF6347; padding: 2px 5px; border-radius: 5px;'>{word}</span> "
            else:
                response_message += f"{word} "

        labels = ['Positive', 'Negative']
        sizes = [positive_percentage, negative_percentage]
        colors = ['#66c2a5', '#fc8d62']
        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'white'}, textprops=dict(color="w"))
        ax.axis('equal')
        plt.title('Sentiment Breakdown', fontsize=14)
        legend_labels = ['Positive', 'Negative']
        legend_handles = [mpatches.Patch(color=color, label=label) for color, label in zip(colors, legend_labels)]
        plt.legend(handles=legend_handles, loc='best', fancybox=True, shadow=True, fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        for i, autotext in enumerate(autotexts):
            autotext.set_color('white')
            autotext.set_fontsize(12)

        st.pyplot(fig)

        return response_message, sentiment_emoji, word_sentiments, num_positive_words, num_negative_words
    except Exception as e:
        return f"An error occurred: {str(e)}", "", {}, 0, 0

def extract_text_from_image(uploaded_image):
    img = Image.open(uploaded_image)
    img = img.convert('RGB')
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([para.get_text() for para in paragraphs])
            return text
        else:
            return "Failed to retrieve the content from the URL."
    except Exception as e:
        return f"An error occurred while fetching the URL content: {str(e)}"

def main():
    st.set_page_config(page_title="Sentiment Analysis", page_icon=":speech_balloon:")

    st.sidebar.info(
        "Welcome to the Sentiment Analysis App! Feel free to express yourself by typing your message, uploading an image, speaking into the microphone, or providing a URL. Click 'Send' to analyze the sentiment and discover the emotions behind your words. Let's explore the sentiment together!"
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Information Insights: This chat app uses VADER Sentiment Analysis to provide sentiment analysis of your messages."
    )
    st.sidebar.markdown("---")
    st.sidebar.subheader("Instructions:")
    st.sidebar.write("1. Use the text area provided to input the text you want to analyze for sentiment. This could be a sentence, a paragraph, or any text you'd like to evaluate.")
    st.sidebar.write("2. Alternatively, you can upload an image containing text. Our app will extract the text from the image and perform sentiment analysis on it.")
    st.sidebar.write("3. You can also click on the microphone button to speak your message. Our app will transcribe your speech and perform sentiment analysis on it.")
    st.sidebar.write("4. You can also provide a URL, and our app will extract the text from the webpage and perform sentiment analysis on it.")
    st.sidebar.write("5. Once you've entered your text, uploaded an image, spoken into the microphone, or provided a URL, click the 'Send' button to initiate the sentiment analysis process.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Features:")
    st.sidebar.write("- Sentiment analysis of user input.")
    st.sidebar.write("- Sentiment emotion support in the form of emoji for easier understanding.")
    st.sidebar.write("- Pie chart visualization for pictorial analysis.")
    st.sidebar.write("- Positive & Negative Word Count for better Sentiment Analysis.")
    st.sidebar.write("- Percentage-based breakdown of positive and negative sentence/paragraph.")
    st.sidebar.write("- Individually highlighted text with different colors in summary.")
    st.sidebar.write("- Supports offline mode for better accessibility.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Limitations:")
    st.sidebar.write("- Currently supports only the English language.")
    st.sidebar.write("- Sometimes may generate inaccurate output.")

    st.title("Welcome To Sentiment Analysis App")
    st.markdown("---")

    input_option = st.radio("Select Input Option:", ("Text", "Image", "Microphone", "URL"))
    
    st.markdown("---")

    if input_option == "Text":
        input_text = st.text_area("You:", "")

        if st.button("Send"):
            response, sentiment_emoji, _, num_positive_words, num_negative_words = detect_sentiment(input_text)
            st.markdown("---")
            st.write(response, unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("Word Count:")
            st.write(f"Number of Positive Words: {num_positive_words}")
            st.write(f"Number of Negative Words: {num_negative_words}")

    elif input_option == "Image":
        uploaded_image = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png"])

        if st.button("Send") and uploaded_image is not None:
            extracted_text = extract_text_from_image(uploaded_image)
            st.markdown("---")
            st.write("Text Extracted from Image:")
            st.write(extracted_text)
            st.write("\n\n")

            response, sentiment_emoji, _, num_positive_words, num_negative_words = detect_sentiment(extracted_text)
            st.write(response, unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("Word Count:")
            st.write(f"Number of Positive Words: {num_positive_words}")
            st.write(f"Number of Negative Words: {num_negative_words}")

    elif input_option == "Microphone":
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Speak now...")
            audio_input = recognizer.listen(source)

        try:
            st.write("Transcribing...")
            spoken_text = recognizer.recognize_google(audio_input)
            st.write("You said:")
            st.write(spoken_text)
            
            response, sentiment_emoji, _, num_positive_words, num_negative_words = detect_sentiment(spoken_text)
            st.markdown("---")
            st.write(response, unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("Word Count:")
            st.write(f"Number of Positive Words: {num_positive_words}")
            st.write(f"Number of Negative Words: {num_negative_words}")

        except sr.UnknownValueError:
            st.write("Sorry, could not understand audio.")
        except sr.RequestError as e:
            st.write(f"Error: {e}")

    elif input_option == "URL":
        url = st.text_input("Enter URL:")

        if st.button("Send"):
            extracted_text = extract_text_from_url(url)
            st.markdown("---")
            st.write("Text Extracted from URL:")
            st.write(extracted_text)
            st.write("\n\n")

            response, sentiment_emoji, _, num_positive_words, num_negative_words = detect_sentiment(extracted_text)
            st.write(response, unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("Word Count:")
            st.write(f"Number of Positive Words: {num_positive_words}")
            st.write(f"Number of Negative Words: {num_negative_words}")

if __name__ == "__main__":
    main()
