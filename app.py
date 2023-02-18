import streamlit as st
from revChatGPT.V1 import Chatbot


st.set_page_config(layout="wide")
access_token = st.secrets['chatbot']['TOKEN']

chatbot = Chatbot(config={
  "access_token": access_token
})
