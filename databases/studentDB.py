from abc import ABC, abstractmethod

class StudentDB(ABC):    
    @abstractmethod
    def create_db(self):
        pass
