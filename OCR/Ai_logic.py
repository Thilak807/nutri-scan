import google.generativeai as genai

class GenaerateResults:  
    def __init__(self, filepath) -> None:
        self.filepath = filepath

    
    def get_answer(self,):
        
        senetence = ""
        with open(self.filepath, 'r') as file:
            senetence = file.read()
        
        genai.configure(api_key="AIzaSyBCcwqQ53hg2wsN7oRzdA9-OtJvnCcQCuw")
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
            }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro-001",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

        convo = model.start_chat(history=[
            ])
        prompt = f"""
                this sentences {senetence} contains names of ingredients or things that are consumed, list the effects of them on human body like smallest negative efffects 
                        """
        convo.send_message(prompt)
        
        response = model.generate_content(prompt)
        return response.text
