import streamlit as st
from revChatGPT.V1 import Chatbot
import pandas as pd
import string
from utils.the_graph import post_query, parse_results
from utils.prompts import protocol_selection_prompt, query_prompt
from utils.urls import URLS
from utils.schemas import SCHEMAS

IMAGE = "https://raw.githubusercontent.com/divesresearch/graph-ai/master/GraphAI-logo.png?token=GHSAT0AAAAAAB3IGMUCZ3NHI477XFDXSRBGY7SLAOA"

st.set_page_config(layout="wide")
access_token = st.secrets['chatbot']['TOKEN']

if 'protocol' not in st.session_state:
    st.session_state.protocol = ''

if 'query' not in st.session_state:
    st.session_state.query = ''

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

if 'df_exists' not in st.session_state:
    st.session_state.df_exists = False

def reset_data():
    st.session_state.protocol = ''
    st.session_state.query = ''
    st.session_state.df = pd.DataFrame()
    st.session_state.df_exists = False

a, b = st.columns([1,9])
a.image(IMAGE, width=110)
b.title("Graph AI\nEasy access to The Graph, powered by AI.")

col1, col2 = st.columns([4,6])
with col1:
    examples = st.radio("Example Prompts:", [
        'show last 1000 swaps of this account on Uniswap: 0x3a8713065e4daa9603b91ef35d6a8336ef7b26c6',
        'show me the latest 50 flashloans on aave.',
        'show the price of the 10 latest sales on decentraland.',
        'I want to write myself'
    ], index=3)

    if examples ==  'I want to write myself':
        input_example = ""
    else:
        input_example = examples
with col2:
    with st.form(key='query_form'):
        user_input = st.text_input("What do you want?", input_example)
        submit_button_1 = st.form_submit_button(label='Submit', on_click=reset_data)

if st.session_state.df_exists or (user_input and submit_button_1):
    chatbot = Chatbot(config={
        "access_token": access_token
    })
    if not st.session_state.protocol:
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

        st.session_state.protocol = protocol.lower()

    schema = SCHEMAS[st.session_state.protocol]

    chatbot = Chatbot(config={
        "access_token": access_token
    })
    if not st.session_state.query:
        with st.spinner(text='Writing the query...'):
            query = ''
            prev_text = ""
            for data in chatbot.ask(
                query_prompt%(st.session_state.protocol, user_input, schema)
            ):
                message = data["message"][len(prev_text):]
                query += message
                prev_text = data["message"]

        st.session_state.query = query[query.find('{'): query.rfind('}') + 1]
    with st.expander(':scroll: Query'):
        st.text(st.session_state.query)

    if not st.session_state.df_exists:
        with st.spinner(text='Sending the request...'):
            results = post_query(URLS[st.session_state.protocol], st.session_state.query)
            if 'data' in results:
                for key, value in results['data'].items():
                    st.session_state.df = pd.DataFrame(parse_results(value))
                st.session_state.df_exists = True
            else:
                st.text(results)

    with st.expander(':scroll: Dataframe', expanded=True):
        st.dataframe(st.session_state.df)

    with st.form(key='chart_form'):
        a, b, c = st.columns([4, 5, 5])
        chart_types = ['Line chart', 'Bar chart']
        chart_type = a.radio('Select one of the following chart types:', chart_types)
        columns = b.multiselect('Select the columns for your plot:', st.session_state.df.columns)
        submit_button_2 = st.form_submit_button(label='Submit')

    if submit_button_2:
        if columns[0].lower() == 'timestamp':
            st.session_state.df[columns[0]] = pd.to_datetime(st.session_state.df[columns[0]], unit='s')
        display_df = st.session_state.df.set_index(columns[0])
        display_df = display_df[columns[1:]]
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(float)
        if chart_type == 'Line chart':
            st.line_chart(display_df)

        if chart_type == 'Bar chart':
            st.bar_chart(display_df)
