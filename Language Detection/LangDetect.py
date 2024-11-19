import tkinter as tk
from tkinter import filedialog
import string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statistics import mean
from googletrans import Translator

# Constants for column names
CNST_TEXT_LINE_NAME = "Input Text"
CNST_TEST_LANGDETECT_LANG_LINE_NAME = "LangDetect: Detected Language"
CNST_TEST_LANGDETECT_PROB_LINE_NAME = "LangDetect: Confidence Score"
CNST_TEST_LANGID_LANG_LINE_NAME = "LangID: Detected Language"
CNST_TEST_LANGID_PROB_LINE_NAME = "LangID: Confidence Score"

# Output file names
CNST_LANG_DETECTION_RESULTS_FILE_NAME = "Language_Detection_Results.csv"
CNST_LANG_DETECTION_DIFFERENCES_FILE_NAME = "Detection_Differences.csv"

# Functions for detection
def detect_language_with_langdetect(line):
    from langdetect import detect_langs
    try:
        langs = detect_langs(line)
        for item in langs:
            return item.lang, item.prob
    except:
        return "Unknown", 0.0

def detect_language_with_langid(line):
    from langid import classify
    lang, prob = classify(line)
    return lang, prob

def translate_text_to_english(text):
    # Initialize the Google Translator
    translator = Translator()
    try:
        # Translate the text to English
        translated = translator.translate(text, dest='en')
        print("")
        return translated.text
    except Exception as e:
        return f"Error in translation: {e}"

def write_data_to_csv(lines, langdetect_lang_results, langdetect_prob_results, langid_lang_results, langid_prob_results):
    data = {
        CNST_TEXT_LINE_NAME: lines,
        CNST_TEST_LANGDETECT_LANG_LINE_NAME: langdetect_lang_results,
        CNST_TEST_LANGDETECT_PROB_LINE_NAME: langdetect_prob_results,
        CNST_TEST_LANGID_LANG_LINE_NAME: langid_lang_results,
        CNST_TEST_LANGID_PROB_LINE_NAME: langid_prob_results
    }
    df = pd.DataFrame(data)
    df.to_csv(CNST_LANG_DETECTION_RESULTS_FILE_NAME, sep="|", index=False)

def extract_differences(file_name):
    df = pd.read_csv(file_name, sep="|")
    differences = df[df[CNST_TEST_LANGDETECT_LANG_LINE_NAME] != df[CNST_TEST_LANGID_LANG_LINE_NAME]]
    differences.to_csv(CNST_LANG_DETECTION_DIFFERENCES_FILE_NAME, sep="|", index=False)

# Visualization for Non-Technical Users
def show_results_for_non_tech_users(file_name):
    df = pd.read_csv(file_name, sep="|")
    sns.set_theme(style="whitegrid")

    print("\nLanguage Detection Results Summary")
    print("=" * 50)

    # Display simple text-based insights
    detected_languages_langdetect = df[CNST_TEST_LANGDETECT_LANG_LINE_NAME].value_counts()
    detected_languages_langid = df[CNST_TEST_LANGID_LANG_LINE_NAME].value_counts()

    print("\nMost Common Languages Detected (LangDetect):")
    print(detected_languages_langdetect)

    print("\nMost Common Languages Detected (LangID):")
    print(detected_languages_langid)

    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Pie chart for LangDetect
    axes[0, 0].set_title("LangDetect - Detected Languages", fontsize=14)
    detected_languages_langdetect.plot.pie(
        autopct='%1.1f%%',
        startangle=90,
        ax=axes[0, 0],
        colors=sns.color_palette("pastel"),
    )
    axes[0, 0].set_ylabel('')

    # Pie chart for LangID
    axes[0, 1].set_title("LangID - Detected Languages", fontsize=14)
    detected_languages_langid.plot.pie(
        autopct='%1.1f%%',
        startangle=90,
        ax=axes[0, 1],
        colors=sns.color_palette("pastel"),
    )
    axes[0, 1].set_ylabel('')

    # Bar chart for LangDetect confidence
    langdetect_mean_probs = df.groupby(CNST_TEST_LANGDETECT_LANG_LINE_NAME)[CNST_TEST_LANGDETECT_PROB_LINE_NAME].mean()
    langdetect_mean_probs.sort_values().plot.barh(ax=axes[1, 0], color="skyblue")
    axes[1, 0].set_title("LangDetect - Mean Confidence Score", fontsize=14)
    axes[1, 0].set_xlabel("Mean Confidence")

    # Bar chart for LangID confidence
    langid_mean_probs = df.groupby(CNST_TEST_LANGID_LANG_LINE_NAME)[CNST_TEST_LANGID_PROB_LINE_NAME].mean()
    langid_mean_probs.sort_values().plot.barh(ax=axes[1, 1], color="skyblue")
    axes[1, 1].set_title("LangID - Mean Confidence Score", fontsize=14)
    axes[1, 1].set_xlabel("Mean Confidence")

    plt.tight_layout()
    plt.savefig("Language_Detection_Visualization.png")
    plt.show()

    print("\nCharts saved as 'Language_Detection_Visualization.png'.")
    print("Detailed results are saved in 'Language_Detection_Results.csv'.")
    print("Any differences are saved in 'Detection_Differences.csv'.")

# Tkinter GUI for showing translations
def show_translation_window(original_texts, translated_texts):
    # Create a new window (Toplevel)
    translation_window = tk.Toplevel()
    translation_window.title("Translation Results")

    # Create a scrollable text box to display the input and translated texts
    text_box = tk.Text(translation_window, wrap=tk.WORD, width=80, height=20)
    text_box.pack(padx=10, pady=10)

    # Display each original and translated pair
    for original, translated in zip(original_texts, translated_texts):
        text_box.insert(tk.END, f"Original: {original}\n")
        text_box.insert(tk.END, f"Translated: {translated}\n")
        text_box.insert(tk.END, "=" * 50 + "\n")

    text_box.config(state=tk.DISABLED)

# Main Workflow
def main():
    # Initialize Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()

    # Ask user to select a file
    file_path = filedialog.askopenfilename()
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    langdetect_lang_results = []
    langdetect_prob_results = []
    langid_lang_results = []
    langid_prob_results = []
    raw_text = []
    translated_texts = []

    # Process lines
    for line in lines:
        line = line.translate(str.maketrans('', '', string.punctuation)).rstrip()
        raw_text.append(line)

        # Translate text to English
        translated_text = translate_text_to_english(line)
        translated_texts.append(translated_text)

        langdetect_lang, langdetect_prob = detect_language_with_langdetect(line)
        langdetect_lang_results.append(langdetect_lang)
        langdetect_prob_results.append(langdetect_prob)

        langid_lang, langid_prob = detect_language_with_langid(line)
        langid_lang_results.append(langid_lang)
        langid_prob_results.append(langid_prob)

    # Show translation window
    show_translation_window(raw_text, translated_texts)

    # Save results to CSV
    write_data_to_csv(raw_text, langdetect_lang_results, langdetect_prob_results, langid_lang_results, langid_prob_results)
    extract_differences(CNST_LANG_DETECTION_RESULTS_FILE_NAME)
    show_results_for_non_tech_users(CNST_LANG_DETECTION_RESULTS_FILE_NAME)

    root.mainloop()

if __name__ == "__main__":
    main()
