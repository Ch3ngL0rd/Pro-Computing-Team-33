from databases.studentDB import StudentDB

from abc import ABC, abstractmethod
import pandas as pd

class File_reader(ABC):
    @abstractmethod
    def extract_data(self, file_path: str) -> pd.DataFrame:
        raise NotImplementedError("method not implemented")
    

    @abstractmethod
    def store_data(self, file_data: pd.DataFrame, student_db: StudentDB) -> None:
        raise NotImplementedError("method not implemented")
