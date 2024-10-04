import requests
import random
import re
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from difflib import SequenceMatcher
import os
import docx
import PyPDF2

def extract_text_from_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(file_path):
    pdf_reader = PyPDF2.PdfFileReader(open(file_path, 'rb'))
    full_text = []
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        full_text.append(page.extract_text())
    return '\n'.join(full_text)

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_random_phrases(text, num_phrases=5):
# Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    # If the number of sentences is less than the requested number of phrases, return all sentences
    if len(sentences) <= num_phrases:
        return sentences
    
    # Randomly select a subset of sentences
    random_phrases = random.sample(sentences, num_phrases)
    return random_phrases

def search_google(query):
    api_key = 'AIzaSyDpszVVzcyrxVRK2wyaWVn62T8G7igkHLc'  # Replace with your actual API key
    cse_id = 'a40e86dec6883429e'  # Replace with your actual CSE ID
    service = build("customsearch", "v1", developerKey=api_key)
    
    try:
        res = service.cse().list(q=query, cx=cse_id).execute()
        return res.get('items', [])
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def scrape_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Implement logic to extract main content from the page
        # For example, you might want to extract text from <p> tags
        paragraphs = soup.find_all('p')
        full_text = ' '.join([para.get_text() for para in paragraphs])
        
        return full_text
    except requests.RequestException as e:
        print(f"An error occurred while scraping {url}: {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred while scraping {url}: {e}")
        return ""

def compare_text(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()