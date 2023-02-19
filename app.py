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

if 'count' not in st.session_state:
    st.session_state.count = 0

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

st.write('Count = ', st.session_state.count)

def increment_counter():
    st.session_state.count += 1

def reset_increment():
    st.session_state.count = 0

examples = st.radio("Example Prompts:", [
    'show last 5 deposit on Uniswap',
    'show me the latest 50 flashloans on aave.',
    'show the price of the 10 latest sales on decentraland.',
    'I want to write myself'
], index=3)

if examples ==  'I want to write myself':
    input_example = ""
else:
    input_example = examples

with st.form(key='query_form'):
    user_input = st.text_input("What do you want?", input_example)
    submit_button_1 = st.form_submit_button(label='Submit', on_click=reset_increment)

if st.session_state.count != 0 or (user_input and submit_button_1):
    if st.session_state.count == 0:
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
                    st.session_state.df = df
            else:
                st.text(results)

        with st.expander(':scroll: Dataframe', expanded=True):
            st.dataframe(df)

    with st.form(key='chart_form'):
        a, b, c = st.columns([4, 5, 5])
        chart_types = ['Line chart', 'Bar chart']
        chart_type = a.radio('Select one of the following chart types:', chart_types)
        columns = b.multiselect('Select the columns for your plot:', st.session_state.df.columns)
        submit_button_2 = st.form_submit_button(label='Submit',on_click=increment_counter)

    if chart_type == 'Line chart' and submit_button_2:
        if columns[0].lower == 'timestamp':
            st.session_state.df[columns[0]] = pd.to_datetime(st.session_state.df[columns[0]])
        st.line_chart(st.session_state.df, x=columns[0], y=columns[1:])

    if chart_type == 'Bar chart' and submit_button_2:
        st.bar_chart(st.session_state.df, x=columns[0], y=columns[1])
