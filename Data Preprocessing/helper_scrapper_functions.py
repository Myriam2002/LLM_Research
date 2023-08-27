import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import os
import PyPDF2
GOLBAL_pages_number = 30
ur_place_of_Tesseract = 'C:/Users/Mariam Barakat/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# ====================================== Scrapping a book that is text 
def extraction_text_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Initialize an empty string to store the extracted text
        extracted_text = ''
        number_of_pages = GOLBAL_pages_number                  ##

        # Loop through each page and extract the text
        for page_num in range(number_of_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            extracted_text+=page_text
       
    return extracted_text

def find_start_and_end(extracted_text): 
    words_to_find_start = ["table of contents", "contents", "index"]
    words_to_find_end = ["chapter 1", "index", "preface", "Summary", "appendix"]
    start = []
    end = []
    for word in words_to_find_start:
        s = extracted_text.lower().find(word)
        if s != -1:
            start.append(s)
    for word in words_to_find_end :
        e = extracted_text.lower().find(word)
        if e != -1:
            end.append(e)
    start = sorted(start, reverse=False)
    end = sorted(end, reverse=True)
    return (start[0],end[0])


def roughly_table_of_content(all_extracted_text):
    start,end = find_start_and_end(all_extracted_text) 

    if start !=-1 and end != -1:
        modified_text = all_extracted_text[start:end]
        return modified_text
    else:
        return all_extracted_text
    
## ====================================== Scrapping a book that is images

def convert_pdf_to_img(pdf_file):
    images = convert_from_path(pdf_file, poppler_path=r"./poppler/poppler-23.08.0/Library/bin", first_page=0, last_page=GOLBAL_pages_number  - 1)
    return images

def convert_image_to_text(file, place_of_Tesseract = ur_place_of_Tesseract):
    pytesseract.pytesseract.tesseract_cmd = place_of_Tesseract
    text = pytesseract.image_to_string(file)
    return text

def extraction_image_pdf(pdf_file):
    images = convert_pdf_to_img(pdf_file)
    final_text = ""
    for img in images:
        out = convert_image_to_text(img)
        final_text += out
    return final_text
## =============================================  Final scrapper

def pdf_to_text(pdf_path):
    all_extracted_text1 = extraction_text_pdf(pdf_path)
    filtered_text = roughly_table_of_content(all_extracted_text1)

    if (all_extracted_text1 == filtered_text):
        all_extracted_text2 = extraction_image_pdf(pdf_path)
        filtered_text = roughly_table_of_content(all_extracted_text2)
    return filtered_text

## ================================== Creating a prompt_template for the output 
def prompt_template(filtered_text):
    prompt_template = "{### Table of contents:" + filtered_text + "}"
    # Path to the text file
    
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the text file
    file_path = os.path.join(script_directory, "book_corpus.txt")
    # Open the file in append mode
    with open(file_path, 'a',encoding='utf-8') as file:
        # Write the string variable to the file
        file.write(prompt_template + '\n')  # Adding a newline character for clarity
    file.close()

## =================================== Loop through the directory to extract all books inside and add to one txt file

def loop_directory_scrapper(path):
    # Loop through PDF files in the directory

    for filename in os.listdir(path):

        if filename.endswith(".pdf"):  # Check if the file is a PDF
            pdf_path = os.path.join(path, filename)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            print("Processing:", pdf_name)

            text = pdf_to_text(pdf_path)
            prompt_template(text)

            print("Finished processing:", pdf_path)

    return 0