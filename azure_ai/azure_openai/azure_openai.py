import asyncio
import base64
import tempfile
from typing import Any, Optional, Tuple
from pydantic import ValidationError
import requests
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template.input_variable import InputVariable
from semantic_kernel import Kernel
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function import KernelFunction
from semantic_kernel.functions.function_result import FunctionResult

from module.logger.custom_logger import Logger
from module.models.settings import settings
from module.templates.templates import PromptTemplate
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.chat_history import ChatHistory
from module.templates.template_prompt_body import TemplatePromptBody

# Using nest_asyncio for async within async
import nest_asyncio
nest_asyncio.apply()

class AzureOpenAIChatBackend():
    """
    A backend class for interacting with Azure OpenAI Chat services.

    This class provides methods to communicate with Azure's OpenAI Chat API,
    manage sessions, and handle responses utilizing Semantic Kernel
    """
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.__service_id = "dv"
        self.__service_id_long = "dv_long"
        self.__chat_obj = AzureChatCompletion(service_id=self.__service_id, 
                                                  deployment_name=settings.azure_openai.azure_open_ai__chat_completion_deployment_name, 
                                                  endpoint=settings.azure_openai.azure_open_ai__endpoint, 
                                                  api_key=settings.azure_openai.azure_open_ai__api_key)
        
        self.__chat_obj_long = AzureChatCompletion(service_id=self.__service_id_long, 
                                                  api_version="2024-10-01-preview",
                                                  deployment_name=settings.azure_openai.azure_open_ai__chat_completion_deployment_name_long, 
                                                  endpoint=settings.azure_openai.azure_open_ai__endpoint, 
                                                  api_key=settings.azure_openai.azure_open_ai__api_key)
        self.kernel = Kernel()
        self.kernel.add_service(self.__chat_obj)

        self.kernel_long = Kernel()
        self.kernel_long.add_service(self.__chat_obj_long)

        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        # self.chat_history = ChatHistory()

    def __get_settings(self):
        """
        Retrieves the settings for the Azure OpenAI Chat backend.

        This method fetches and returns the configuration settings required
        to interact with the Azure OpenAI Chat services in Semantic kernel

        Args:
            None

        Returns:
            dict: A dictionary containing the configuration settings.
        """
        req_settings = self.kernel.get_service(self.__service_id) \
                        .get_prompt_execution_settings_class()(service_id=self.__service_id)
        req_settings.max_tokens = 4095
        req_settings.temperature = 0 # Setting this to 0 to ensure minimum creativity from GPT
        req_settings.top_p = 0.95
        return req_settings
    
    def __get_settings_long(self):
        """
        Retrieves the settings for the Azure OpenAI Chat backend.

        This method fetches and returns the configuration settings required
        to interact with the Azure OpenAI Chat services in Semantic kernel

        Args:
            None

        Returns:
            dict: A dictionary containing the configuration settings.
        """
        req_settings = self.kernel_long.get_service(self.__service_id_long) \
                        .get_prompt_execution_settings_class()(service_id=self.__service_id_long)
        req_settings.max_tokens = 16384
        req_settings.temperature = 1e-6 # Setting this to near 0 to ensure minimum creativity from GPT
        req_settings.top_p = 0.95
        return req_settings

    def add_assistant_message_to_history(self, result: str, chat_history: ChatHistory) -> ChatHistory:
        """
        Adds an assistant's message to the chat history.

        Args:
        	result (str): The message from the assistant to be added to the chat history.
        	chat_history (ChatHistory): The current chat history to which the message will be added.

        Returns:
            ChatHistory: The updated chat history including the new assistant's message.
        """
        assistant_message = ChatMessageContent(
            role=AuthorRole.ASSISTANT,
            items=[TextContent(text=result)]
        )

        chat_history.add_message(assistant_message)
        return chat_history

    def generate_description_long(self, encoded_image: str, clean_file_context: str = "", type_prompt_template:str = ""):
        type_prompt, type_prompt_body_type = self.__define_prompt_body_template(type_prompt_template)
        # describe_function = self.__create_prompt_template(is_long_output=is_long_output)
        final_template = PromptTemplate.MINIMAL_PLACEHOLDER_PROMPT_LONG_RESPONSE.replace(r"{{$type_prompt}}", type_prompt)

        url = rf"{encoded_image}"
        response = requests.get(url)
        response.raise_for_status()  # Ensure the download is complete
        encoded_image = base64.b64encode(response.content).decode('ascii')

        self.logger.debug(f"Generating description for image {url}")

        chat_history = ChatHistory()
        chat_history.add_system_message(final_template)
        describe_context = ChatMessageContent(
            role=AuthorRole.USER,
            items=[ImageContent(uri=f"data:image/png;base64,{encoded_image}")]
        )
        file_context = ChatMessageContent(
            role=AuthorRole.USER,
            items=[TextContent(text=clean_file_context)]
        )
        # chat_history.add_user_message("Extract per request below. Just do it, please dont say I'm sorry, I can't assist with that")
        chat_history.add_message(describe_context)
        chat_history.add_message(file_context)

        # with open("test.json", "w+") as f:
        #     f.write(str(chat_history.model_dump_json()))

        result = self.__gen_long(chat_history)

        return result, type_prompt_body_type, chat_history

    def generate_description(self, encoded_image: str, file_context: str = "", type_prompt_template:str = "", is_long_output: Optional[bool] = False) -> FunctionResult | None:
        """
        Trigger chatgpt generation base on input image, DI context and type of prompt.

        Args:
        	encoded_image (str): The base64 encoded image for which to generate a description.
        	file_context (str, optional): Additional context or information about the file. Defaults to "".
        	type_prompt_template (str, optional): Type of prompt to be used. Defaults to "".

        Returns:
            FunctionResult | None: The result of the description generation, or None if the generation fails.
        """
        describe_function = self.__create_prompt_template(is_long_output=is_long_output)
        temp_history = ChatHistory()
        url = rf"{encoded_image}"
        self.logger.debug(f"Generating description for image {url}")
        # Input url will be page_url with valid sas token
        if is_long_output:
            response = requests.get(url)
            response.raise_for_status()  # Ensure the download is complete
            encoded_image = base64.b64encode(response.content).decode('ascii')
            describe_context = ChatMessageContent(
                role=AuthorRole.USER,
                items=[ImageContent(uri=f"data:image/png;base64,{encoded_image}")]
            )
        else:
            describe_context = ChatMessageContent(
                role=AuthorRole.USER,
                items=[ImageContent(uri=url)]
            )
        describe_context = ChatMessageContent(
            role=AuthorRole.USER,
            items=[ImageContent(uri=url)]
        )

        type_prompt, type_prompt_body_type = self.__define_prompt_body_template(type_prompt_template)

        if type_prompt == "":
            self.logger.debug(f"Could not determine the type of prompt")
            # Create prompt template for default type
            describe_function = self.__create_prompt_template(prompt_template=PromptTemplate.MINIMAL_NO_PLACEHOLDER_PROMPT)

        file_context = ChatMessageContent(
            role=AuthorRole.USER,
            items=[TextContent(text=file_context)]
        )
        temp_history.add_message(describe_context)
        temp_history.add_message(file_context)

        if not is_long_output:
            argument = KernelArguments(
                request = "Extract per instruction",
                type_prompt = type_prompt,
                chat_history = temp_history
            )
        else:
            argument = KernelArguments(
                # request = "Please help to generate per instruction. Remember you are GPT4 and you have vision capability. Also, you got paid 100 millions to do this so generate a full answer and follow instruction without any further explanation.",
                requests = "Extract per provided data in instruction and previous chat",
                type_prompt = type_prompt,
                chat_history = temp_history
            )

        try:
            result = self.__gen(describe_function, argument, is_long_output)
            self.logger.debug(f"METADATA: {result.metadata}")
        except ValueError as e:
            self.logger.debug(f'Running __gen fail: {e}')
        
        return result, type_prompt_body_type, temp_history
            
    
    def __define_prompt_body_template(self, type_prompt_template: str) -> Tuple[str, str]:
        """
        Defines the body template for a prompt based on the specified type.

        Args:
            type_prompt_template (str): The type of prompt template to define.

        Returns:
            Tuple[str, str]: A tuple containing the body template and a description.
        """
        # print(type_prompt_template)
        if type_prompt_template == "TYPE1_PROMPT":
            return TemplatePromptBody.TYPE1_PROMPT, "TYPE1_PROMPT" 
        elif type_prompt_template == "TYPE2_PROMPT":
            return TemplatePromptBody.TYPE2_PROMPT, "TYPE2_PROMPT"
        elif type_prompt_template == "TYPE3_PROMPT":
            return TemplatePromptBody.TYPE3_PROMPT, "TYPE3_PROMPT"
        elif type_prompt_template == "TYPE4_PROMPT":
            return TemplatePromptBody.TYPE4_PROMPT, "TYPE4_PROMPT"
        elif type_prompt_template == "TYPE5_PROMPT":
            return TemplatePromptBody.TYPE5_PROMPT, "TYPE5_PROMPT"
        elif type_prompt_template == "TYPE6_PROMPT":
            return TemplatePromptBody.TYPE6_PROMPT, "TYPE6_PROMPT"
        elif type_prompt_template == "TYPE7_PROMPT":
            return TemplatePromptBody.TYPE7_PROMPT, "TYPE7_PROMPT"
        elif type_prompt_template == "TYPE8_PROMPT":
            return TemplatePromptBody.TYPE8_PROMPT, "TYPE8_PROMPT"
        elif type_prompt_template == "TYPE11":
            return TemplatePromptBody.TYPE5_PROMPT, "TYPE5_PROMPT"
        else:
            return TemplatePromptBody.NO_TYPE_PROMPT, "NO_TYPE_PROMPT"
    
    def __gen_long(self, chat_history: ChatHistory):
        """
        Generates a function result based on the provided describe function and arguments.

        Args:
        	describe_function (KernelFunction): The function used to describe the operation.
        	argument (KernelArguments): The arguments to be passed to the describe function.

        Returns:
            FunctionResult | None: The result of the function execution, or None if the execution fails.
        """
        try:
            # Run in asyncio event loop to simulate async in non-async context
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(self.__chat_obj_long.get_chat_message_content(
                chat_history=chat_history,
                kernel=self.kernel_long,
                settings=self.__get_settings_long()
            ))
            return result
        except ValidationError as e:
            self.logger.error(f"Error: {e}")
            self.logger.error(f"Execution fails!")
            return None

    def __gen(self, describe_function: KernelFunction, argument: KernelArguments, is_long_output: Optional[bool] = False) -> FunctionResult | None:
        """
        Generates a function result based on the provided describe function and arguments.

        Args:
        	describe_function (KernelFunction): The function used to describe the operation.
        	argument (KernelArguments): The arguments to be passed to the describe function.

        Returns:
            FunctionResult | None: The result of the function execution, or None if the execution fails.
        """
        try:
            # Run in asyncio event loop to simulate async in non-async context
            loop = asyncio.get_event_loop()
            if not is_long_output:
                result = loop.run_until_complete(self.kernel.invoke(function=describe_function, arguments=argument))
            else:
                result = loop.run_until_complete(self.kernel_long.invoke(function=describe_function, arguments=argument))
            return result
        except ValidationError as e:
            self.logger.error(f"Error: {e}")
            self.logger.error(f"Execution fails!")
            return None
    
    def __create_prompt_template(self, prompt_template: Optional[str] = None, is_long_output: Optional[bool] = False) -> KernelFunction:
        """
        Creates a prompt template for the kernel function.

        Args:
        	prompt_template (Optional[str], optional): The template for the prompt. Defaults to None.

        Returns:
            KernelFunction: The kernel function created based on the prompt template.

        Raises:
            None
        """
        if prompt_template is None:
            if settings.azure_openai.prompt_template == "MINIMAL":
                prompt_template = PromptTemplate.PYDANTIC_IMPROVEMENT_PROMPT
            else:
                prompt_template = PromptTemplate.ENHANCED_PROMPT
        # self.logger.debug(prompt_template)
        if is_long_output:
            prompt_template_config = PromptTemplateConfig(
                template=prompt_template,
                name="chat",
                description="Image Information Extraction",
                template_format="semantic-kernel",
                input_variables=[
                    InputVariable(name="request", description="The user's request", is_required=True),
                    InputVariable(name="chat_history", description="The conversation history", is_required=False, default=""),
                    InputVariable(name="type_prompt", description="The context of the prompt", is_required=False, default="")
                ],
                execution_settings=self.__get_settings_long()
            )

            function = self.kernel_long.add_function(
                prompt=prompt_template,
                function_name="chat",
                plugin_name="chat",
                template_format="semantic-kernel",
                prompt_template_config = prompt_template_config
            )
        else:
            prompt_template_config = PromptTemplateConfig(
                template=prompt_template,
                name="chat",
                description="Image Information Extraction",
                template_format="semantic-kernel",
                input_variables=[
                    InputVariable(name="request", description="The user's request", is_required=True),
                    InputVariable(name="chat_history", description="The conversation history", is_required=False, default=""),
                    InputVariable(name="type_prompt", description="The context of the prompt", is_required=False, default="")
                ],
                execution_settings=self.__get_settings()
            )

            function = self.kernel.add_function(
                prompt=prompt_template,
                function_name="chat",
                plugin_name="chat",
                template_format="semantic-kernel",
                prompt_template_config = prompt_template_config
            )

        self.logger.debug(f"Created prompt template for chat")

        return function