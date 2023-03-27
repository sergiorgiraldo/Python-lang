import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Get input text from the console
input_text = input("Enter the text to be converted to leet speak: ")

# Create the prompt
prompt = f"Convert the following text into leet speak:\n\n{input_text}\n\nLeet speak:"

response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.5,
    max_tokens=100,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    n=1,
)

leet_text = response.choices[0].text.strip()
print("Leet speak version:", leet_text)
