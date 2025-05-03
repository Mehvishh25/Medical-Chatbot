import os
GROQ_API_KEY=os.environ.get('GROQ_API_KEY')

import base64


#image_path='acne.jpg'
def encode_image(image_path):      
    image_file=open(image_path,'rb')
    return base64.b64encode(image_file.read()).decode('utf-8')

from groq import Groq

query = (
    "Act like a qualified medical doctor. Carefully analyze the image provided and describe the visible medical issue. "
    "If you can confidently identify it, provide possible causes, home care suggestions, and explain when medical help is needed. "
    "If you are uncertain or the image is unclear, explicitly say 'I do not know' and strongly recommend seeking professional medical assistance "
    "rather than guessing or making assumptions."
)
model='meta-llama/llama-4-maverick-17b-128e-instruct'

def analyze_image(query,model,encoded_img):
    
    client=Groq()

    messages=[
        {
            'role':'user',
            'content':[
                {
                    'type': 'text',
                    'text': query
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{encoded_img}'
                    }
                }
            ]
        }
    ]

    try:
        chat_completion = client.chat.completions.create(model=model, messages=messages)
        print(chat_completion.choices[0].message.content)  # Add debug logging
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return "Error in processing image"