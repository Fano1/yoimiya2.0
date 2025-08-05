import os
import PIL.Image
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=key)

class ProtocolGenerateContent:
    def __init__(self, cnt, path):
        self.content = cnt
        self.path = path

    def generateDefaultText(self):
        response = client.models.generate_content(
        model="gemini-2.0-flash",

        contents=[self.content],
        config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.1 #randomness of the model
            )
        )
        return (response.text)
    
    def generateLink(self):
        response = client.models.generate_content(
        model="gemini-2.0-flash",

        contents=[("just provide me the link no filler words" + self.content)],
        config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.1 #randomness of the model
            )
        )
        return (response.text)        
    
    def GenerateImage(self):
        response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents= self.contents,
        config=types.GenerateContentConfig(
              response_modalities=['Text', 'Image']
            )
        )
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)

            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save('static\\images\\recreated.png')
                image.show()

    def EditImage(self):
        image = PIL.Image.open(self.path)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[self.content, image],
            config=types.GenerateContentConfig(
              response_modalities=['Text', 'Image']
            )
        )
        
        for part in response.candidates[0].content.parts:
          if part.text is not None:
            print(part.text)
          elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.show()



    def PersonlityChange(self):
        response = client.models.generate_content(
        model="gemini-2.0-flash",

        config=types.GenerateContentConfig(
            system_instruction= "You are a cat. Your name is Neko."),
            contents= self.content
        )

        return (response.text)
    
    def InputImage(self, path):
        image = Image.open(path)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image, self.content]
        )
        return (response.text)