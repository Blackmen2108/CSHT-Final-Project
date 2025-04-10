from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from azure_ai.template.prompt_template import PromptTemplate
from settings.settings import azure_settings


class GPTComponent:
    def __init__(self):
        self.llm_model = self.__get_llm_model()

    def __get_llm_model(
        self, t: float = 0.0, max_output_token: int = None
    ) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            azure_endpoint=azure_settings.openai_settings.azure_open_ai__endpoint,
            api_key=azure_settings.openai_settings.azure_open_ai__api_key,
            api_version="2024-10-01-preview",
            azure_deployment=azure_settings.openai_settings.azure_open_ai__chat_completion_deployment_name,
            temperature=1e-6,
            max_tokens=None,
            top_p=0.95,
            timeout=60,
            seed=42
        )


# if __name__ == "__main__":
#     import base64
#     import json
#     from module.models.other import MainInformation, Entity

#     gpt = GPTComponent()
#     die_json_path = "e2b2b05439e6d3c7b69de516fd888cb865fdee9b-0.json"
#     image_path = f"e2b2b05439e6d3c7b69de516fd888cb865fdee9b-0.png"

#     die_json = None
#     image_bytes = None
#     with open(die_json_path, "r", encoding="utf-8") as file:
#         die_json = json.load(file)

#     with open(image_path, "rb") as file:
#         image_bytes = file.read()

#     encoded_image = base64.b64encode(image_bytes).decode("ascii")
#     msg = [
#         SystemMessage(content=PromptTemplate.MAIN_TEMPLATE),
#         HumanMessage(
#             content=[
#                 # FIXME: this DIE message is not good for now
#                 {"type": "text", "text": die_json["content"]},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "data:{mime};base64,{base64_image}".format(
#                             mime="image/png",
#                             base64_image=encoded_image,
#                         ),
#                         "detail": "low",
#                     },
#                 },
#             ]
#         ),
#     ]
#     response = gpt.llm_model.invoke(msg)
#     response = response.content
#     with open("response.python.txt", "w", encoding="utf-8") as file:
#         file.write(response)
#         pass
#     __clean = response.replace("```python", "").replace("```", "").strip()
#     # FIXME: remove eval to a safer option
#     main_information = eval(__clean)
#     data = MainInformation(**main_information.model_dump())
#     with open("response.parsed.json", "w", encoding="utf-8") as file:
#         file.write(data.model_dump_json(indent=4))
#         pass
