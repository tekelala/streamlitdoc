import streamlit as st
import requests
import json

def send_message(prompts):
    api_url = "https://api.anthropic.com/v1/complete"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": st.secrets["API_KEY"]  
    }
    
    # Read developer-focused context from file
    with open("streamlitdocumentation.txt") as f:
        context = f.read() 
    
    # Update conversation prefix 
    conversation = "\n\n".join([f'{item["role"]}: {item["content"]}' for item in prompts]) + "\n\nClaude (Developer Assistant):"  
    
    # Define the body of the request 
    body = {
        "prompt": conversation,
        "model": "claude-v1.3-100k",  # Update model if new version is released
        "context": context,  
        "max_tokens_to_sample": 1000,
        "stop_sequences": ["\n\nHuman:"]
    }
    
    # Make a POST request to the Claude API 
    response = requests.post(api_url, headers=headers, data=json.dumps(body))
    response.raise_for_status()
    return response.json()


# Container for Title and Banner
with st.container():
    st.title("Chat with Claude")
    st.write("Welcome to our chat app!")  # Welcome message
    # st.image("banner.jpg")  # Display a banner (uncomment this line and replace "banner.jpg" with the path to your banner image)

# Define initial prompts
if "prompts" not in st.session_state:
    st.session_state.prompts = [
        {
           "role": "Human", 
           "content": "I'm building an application in Python using Streamlit and want your advice." 
        }
    ] 

# Container for conversation history
with st.container():
    # Display the entire conversation
    for prompt in st.session_state.prompts:
        if prompt['role'] == 'Human':
            st.write(f"You: {prompt['content']}")
        else:  # prompt['role'] == 'Assistant'
            st.write(f"Claude: {prompt['content']}")

# Container for user input and Send button
with st.container():
    with st.form(key='message_form'):
        user_message = st.text_input("You: ", key=f"user_input_{len(st.session_state.prompts)}")
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_message:
            st.session_state.prompts.append({
                "role": "Human",
                "content": user_message
            })

            if st.session_state.prompts:
                with st.spinner('Waiting for Claude...'):
                    try:
                        result = send_message(st.session_state.prompts)

                        # Append Claude's response to the prompts
                        st.session_state.prompts.append({
                            "role": "Assistant",
                            "content": result['completion']
                        })

                        # Rerun the script to update the chat
                        st.experimental_rerun()

                        # Display a success message
                        st.success("Message sent successfully!")

                    except requests.exceptions.HTTPError as errh:
                        st.error(f"HTTP Error: {errh}")
                    except requests.exceptions.ConnectionError as errc:
                        st.error(f"Error Connecting: {errc}")
                    except requests.exceptions.Timeout as errt:
                        st.error(f"Timeout Error: {errt}")
                    except requests.exceptions.RequestException as err:
                        st.error(f"Something went wrong: {err}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

# Container for Restart button
with st.container():
    if st.button('Restart'):
        st.session_state.prompts = []
        st.experimental_rerun()