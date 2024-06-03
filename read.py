import json

def file_reading(file_name: str) :
  with open(file_name, 'r', encoding='utf-8') as file:
    return json.load(file)

def file_print(file_name: str, data) :
  with open(file_name, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)