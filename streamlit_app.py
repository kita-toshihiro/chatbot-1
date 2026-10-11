import streamlit as st
from google import genai
from google.genai import types

# Show title and description.
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Gemini's model to generate responses. "
    "You can learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Fetch the Gemini API key from Streamlit secrets.
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Gemini API key is not set. Please add `GEMINI_API_KEY` to your Streamlit secrets.", icon="⚠️")
    st.stop()

gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Create a Gemini client.
client = genai.Client(api_key=gemini_api_key)

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert Streamlit message history to Gemini chat history format.
    history = []
    for m in st.session_state.messages[:-1]:
        gemini_role = "user" if m["role"] == "user" else "model"
        history.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=m["content"])]
            )
        )

    # Create a chat session with history.
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=history
    )

    # Generate a response using streaming.
    response_stream = chat.send_message_stream(prompt)

    def stream_generator():
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    # Stream the response to the chat, then store it in session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream_generator())
        
    st.session_state.messages.append({"role": "assistant", "content": response})
