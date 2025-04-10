from settings.config.azure_blob import AzureBlobStorageSettings
from settings.config.logger import LoggerSettings
from settings.config.azure_openai import AzureOpenAISettings
from settings.config.pdf_processor import PDFProcessorSettings
from settings.config.azure_document_intel import AzureDocumentIntelligenceSettings

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Settings(metaclass=SingletonMeta):
    def __init__(self):
        self.blob = AzureBlobStorageSettings()
        self.logger_setting = LoggerSettings()
        self.openai_settings = AzureOpenAISettings()
        self.pdf_processor = PDFProcessorSettings()
        self.di_settings = AzureDocumentIntelligenceSettings()
        
azure_settings = Settings()