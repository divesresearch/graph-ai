import streamlit as st
from revChatGPT.V1 import Chatbot
import pandas as pd
import string
from utils.the_graph import post_query, parse_results
from utils.prompts import protocol_selection_prompt, query_prompt
from utils.urls import URLS
from utils.schemas import SCHEMAS

st.set_page_config(layout="wide")
access_token = st.secrets['chatbot']['TOKEN']

with st.form(key='query_form'):
    user_input = st.text_input("What do you want?")
    submit_button = st.form_submit_button(label='Submit')

if user_input:
    chatbot = Chatbot(config={
        "access_token": access_token
    })
    with st.spinner(text='Detecting the protocol...'):
        protocol = ''
        prev_text = ""
        for data in chatbot.ask(
            protocol_selection_prompt%(user_input)
        ):
            message = data["message"][len(prev_text) :]
            protocol += message
            prev_text = data["message"]

    for char in string.punctuation:
        protocol = protocol.replace(char, '')
    protocol = protocol.lower()

    schema = SCHEMAS[protocol]

    chatbot = Chatbot(config={
        "access_token": access_token
    })
    with st.spinner(text='Writing the query...'):
        response = ''
        prev_text = ""
        for data in chatbot.ask(
            query_prompt%(protocol, user_input, schema)
        ):
            message = data["message"][len(prev_text):]
            response += message
            prev_text = data["message"]

    query = response[response.find('{'): response.rfind('}') + 1]
    with st.expander(':scroll: Query'):
        st.text(query)

    with st.spinner(text='Sending the request...'):
        results = post_query(URLS[protocol], query)
        if 'data' in results:
            for key, value in results['data'].items():
                df = pd.DataFrame(parse_results(value))
        else:
            st.text(results)

    with st.expander(':scroll: Dataframe', expanded=True):
        st.dataframe(df)

    with st.form(key='chart_form'):
        a, b, c = st.columns([4, 5, 5])
        chart_types = ['Line chart', 'Bar chart', 'Pie chart']
        chart_type = a.radio('Select one of the following chart types:', chart_types)
        columns = b.multiselect('Select the columns for your plot:', df.columns)
        submit_button = st.form_submit_button(label='Submit')
