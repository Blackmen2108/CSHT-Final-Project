
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class PDFProcessorSettings(BaseSettings):
    pdf_processor_thread_count: Optional[int] = Field(..., 
                    env='PDF_PROCESSOR_THREAD_COUNT', 
                    description="Number of thread to use for PDF processing. \
                    Set to -1 for auto detect", 
                    # default=-1, 
                    frozen=True)
    pdf_processor_dpi: Optional[int] = Field(..., 
                    env='PDF_PROCESSOR_DPI', 
                    description="DPI for PDF processing. Default is 200. \
                    The higher the DPI, the better the quality of the image, \
                    but the slower the processing speed.", 
                    # default=200, 
                    frozen=True)