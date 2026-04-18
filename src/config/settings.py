import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR = os.getcwd()

    @classmethod 
    def get_dir(cls, *args) -> str: 
        path = cls.BASE_DIR 
        for value in args: 
            path = os.path.join(path, value) 
        return path
    
    @classmethod
    def create_dir(cls, *args):
        print(f"DIR PATHS ----> {args}")
        base_dir = cls.BASE_DIR
        new_path = '\\'.join(args)
        new_dir = os.path.join(base_dir, new_path)
        print(f"NEW DIR ------> {new_dir}")
        os.makedirs(new_dir, exist_ok=True)
        return new_dir