from dataclasses import dataclass 
 
 
@dataclass 
class Mail: 
    filename: str 
    subject: str 
    sender: str 
    body: str 
 
    def is_empty(self) -> bool: 
        return len(self.body.strip()) == 0