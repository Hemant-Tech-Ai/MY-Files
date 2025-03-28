from typing import Optional
from pydantic import BaseModel

class PDFMinerConfig(BaseModel):
    """Configuration for PDFMiner settings.
    
    This class is used to configure the PDFMiner library's behavior when processing PDFs.
    It allows customization of text extraction parameters.
    """
    line_overlap: Optional[float] = None
    word_margin: Optional[float] = None
    line_margin: Optional[float] = None
    char_margin: Optional[float] = None