from abc import ABC, abstractmethod

class StudentDB(ABC):    
    @abstractmethod
    def create_db(self):
        raise NotImplementedError("method not implemented")
    

    @abstractmethod
    def truncate_db(self):
        raise NotImplementedError("method not implemented")


    @abstractmethod
    def add_student(self):
        raise NotImplementedError("method not implemented")


    @abstractmethod
    def add_unit(self):
        raise NotImplementedError("method not implemented")


    @abstractmethod
    def add_enrollment(self):
        raise NotImplementedError("method not implemented")
