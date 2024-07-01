from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
import nltk
import re
import streamlit as st
from openpyxl.chart import DoughnutChart, Reference, PieChart, PieChart3D
from textblob import TextBlob
import pandas as pd

import openpyxl
import matplotlib.pyplot as plt
# Download NLTK
nltk.download('vader_lexicon')

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

#initialize xlsx file
#df = pd.read_excel('comments.xlsx', usecols=['like_count', 'text'])

def clean_text(text):
    # Remove non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return cleaned_text

def remove_urls(text):
    # Remove URLs using regex
    cleaned_text = re.sub(r'http\S+', '', text)
    return cleaned_text

def tokenize_text(text):
    tokens = word_tokenize(text)
    return tokens

def analyse_comments(df):
    value = []
    likes = []
    positive_counter = 0
    negative_counter = 0
    neutral_counter = 0
    consent = [
        {"PositiveConsent": '', "likes": 0},
        {"NegativeConsent": '', "likes": 0}
    ]

    for index, row in df.iterrows():

        #clean text from all links
        no_url_comment = remove_urls(row['text'])

        #clean text from all special characters
        cleaned_comment = clean_text(no_url_comment)

        
        value.append(sia.polarity_scores(cleaned_comment))
        likes.append(row['like_count'])

        if sia.polarity_scores(cleaned_comment)['compound'] > 0.5:
            positive_counter +=1
            if(row['like_count'] > 1):
                positive_counter += row['like_count']
            if(row['like_count'] > consent[0]['likes']):
                consent[0]['PositiveConsent'] = row['text']
                consent[0]['likes'] = row['like_count']

        elif sia.polarity_scores(cleaned_comment)['compound'] < -0.2:
            negative_counter += 1
            if (row['like_count'] > 1):
                negative_counter += row['like_count']
            if (row['like_count'] > consent[1]['likes']):
                consent[1]['NegativeConsent'] = row['text']
                consent[1]['likes'] = row['like_count']
        else:
            neutral_counter += 1
            if (row['like_count'] > 1):
                neutral_counter += row['like_count']

        print(row['text'], " ---", sia.polarity_scores(cleaned_comment)['compound'])

    write_results(df, value, likes, positive_counter, negative_counter, neutral_counter, consent)


def write_results(df, value, likes, positive_counter, negative_counter, neutral_counter, consent):
    df_new = pd.DataFrame(value)
    with pd.ExcelWriter('comments.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_new.to_excel(writer, sheet_name='analysis', index=False)
        df_new['likes'] = likes

    # Create a new DataFrame (for illustration purposes)
    df_new['likes'] = likes

    # Write data to the new worksheet
    with pd.ExcelWriter('comments.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Write the new DataFrame to a new sheet
        df_new.to_excel(writer, sheet_name='analysis', index=False)

    '''data = {'positive': positive_counter,
            'negative': negative_counter,
            'neutral': neutral_counter}'''

    data = [
        ['positive', positive_counter],
        ['negative', negative_counter],
        ['neutral', neutral_counter],
    ]

    i = ['positive', 'negative', 'neutral']  # Specify an index
    df_new = pd.DataFrame(data, columns=["value", "number"])

    with pd.ExcelWriter('comments.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Write the new DataFrame to a new sheet
        df_new.to_excel(writer, sheet_name='end', index=False)

    # Access the openpyxl workbook and worksheet objects from the dataframe
    workbook = writer.book
    worksheet = writer.sheets['end']

    # Create a ring chart
    chart = PieChart()

    labels = Reference(worksheet, min_col=1, min_row=2, max_row=4)
    data = Reference(worksheet, min_col=2, min_row=1, max_row=4)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labels)

    #-------------------STREAMLIT---------------------
    st.subheader("Pie Chart")
    pie_chart_data = data
    plt.pie([positive_counter,negative_counter,neutral_counter], labels=i)
    st.pyplot(plt)
    #-------------------------------------------------
    # Insert the chart into the worksheet
    worksheet.add_chart(chart, 'E1')
    workbook.save('comments.xlsx')

    data = [
        ["Positive", consent[0]['PositiveConsent'], consent[0]['likes']],
        ['Negative', consent[1]['NegativeConsent'], consent[1]['likes']],
    ]
    df_new = pd.DataFrame(data, columns=["value", "comment", "likes"])
    with pd.ExcelWriter('comments.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_new.to_excel(writer, sheet_name='stats', index=False)


    st.subheader("Most influential comments")
    st.write(df_new)

    with open("comments.xlsx", "rb") as template_file:
        template_byte = template_file.read()

    st.download_button(label="Click to Download Template File",
                       data=template_byte,
                       file_name="youtube_stats.xlsx",
                       mime='application/octet-stream')

#analyse_comments(df)







