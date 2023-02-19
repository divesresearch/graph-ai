import streamlit as st
from revChatGPT.V1 import Chatbot
import pandas as pd
from utils.the_graph import post_query, parse_results
from utils.prompts import protocol_selection_prompt, query_prompt
from utils.urls import URLS
from utils.schemas import SCHEMAS

st.set_page_config(layout="wide")
access_token = st.secrets['chatbot']['TOKEN']

user_input = st.text_input("What do you want?")

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

    st.text(protocol.lower())

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

    st.text(response[:100])
    query = response[response.find('{'), response.rfind('}')]

    with st.spinner(text='Sending the request...'):
        results = post_query(URLS[protocol], query)
        if 'data' in results:
            for key, value in results['data'].items():
                df = pd.DataFrame(parse_results(value))
        else:
            st.text(results)

    st.dataframe(df)
