import streamlit as st
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Set up the environment for the Google API
os.environ["GOOGLE_API_KEY"] ="AIzaSyAVp4msvwc8J5XEJ4S6k3Mchzm86VIZYlg"

# Initialize the chat model
chat = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.8,
    max_tokens=None,
    timeout=None,
    max_retries=2
    # other params...
)

# Streamlit UI setup
st.set_page_config(page_title="Conversational Q&A Chatbot")
st.header("cric🏏 chatbot")

# Define the prompt message for the AI
prompt_message = """
You are a cricket AI assistant. Provide detailed and well-formatted responses about cricketers, including bullet points for records and key information. 
Here are a few examples which you should apply for only professional cricketers:

Example 1:
- **Name**: Sachin Tendulkar
- **Country**: India
- **Records**: Most centuries in international cricket, most runs in ODIs
- **About**: Known as the 'Little Master,' Sachin is regarded as one of the greatest batsmen of all time.

Example 2:
- **Name**: Virat Kohli
- **Country**: India
- **Records**: Fastest to 8000, 9000, 10,000 runs in ODIs
- **About**: Renowned for his aggressive batting and leadership skills. He has been a key player for India across formats.

Provide responses in a similar format for any cricketer or cricket-related queries.
"""

# Initialize session state with examples for few-shot prompting and message history
if 'flowmessages' not in st.session_state:
    st.session_state['flowmessages'] = [SystemMessage(content=prompt_message)]
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Function to get chat model response
def get_chatmodel_response(question):
    # Append the user's question to the message flow
    st.session_state['flowmessages'].append(HumanMessage(content=question))
    
    # Get the response from the chat model
    response = chat(st.session_state['flowmessages'])
    
    # Append the model's response to the message flow
    st.session_state['flowmessages'].append(AIMessage(content=response.content))
    
    return response.content

# Input field and submit button in the Streamlit app
input = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# Handle form submission
if submit:
    if input.lower() in ["clear memory, clear chat", "clear history"]:
        # Reset flowmessages while preserving the SystemMessage
        st.session_state['flowmessages'] = [SystemMessage(content=prompt_message)]
        st.session_state['history'] = []
        st.write("History cleared.")
    else:
        # Get the response from the chat model
        response = get_chatmodel_response(input)

        # Add the question and response to history
        st.session_state['history'].append({"question": input, "response": response})

        # Display the response
        st.subheader("The Response is")
        st.write(response)

# Display conversation history, excluding the current interaction and reversing the order
if st.session_state['history']:
    # Exclude the most recent entry and reverse the order of the history
    for item in reversed(st.session_state['history'][:-1]):
        st.write(f"**Q:** {item['question']}")
        st.write(f"**A:** {item['response']}")