class InvalidConfigException(Exception):
    """Custom Exception for specific error handling"""
    
    def __init__(self, message="There was an error"):
        self.message = message
        super().__init__(self.message)
