import streamlit as st
from google import genai
from google.genai import types

# Show title and description.
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Gemini's model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get from Google AI Studio. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:

    # Create a Gemini client.
    client = genai.Client(api_key=gemini_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Convert Streamlit message history to Gemini chat history format.
        # Exclude the latest prompt since it will be sent via send_message_stream.
        history = []
        for m in st.session_state.messages[:-1]:
            gemini_role = "user" if m["role"] == "user" else "model"
            history.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=m["content"])]
                )
            )

        # Create a chat session with history using the new SDK.
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=history
        )

        # Generate a response using streaming via send_message_stream.
        response_stream = chat.send_message_stream(prompt)

        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
            
        st.session_state.messages.append({"role": "assistant", "content": response})
