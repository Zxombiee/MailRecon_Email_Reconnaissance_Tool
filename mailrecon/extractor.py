import re 
from urllib.parse import unquote 

from bs4 import BeautifulSoup  # untuk baca HTML page

#variable
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}") #untuk check email pattern
AT_PATTERN = re.compile(r"\s*[\[\(\{]\s*at\s*[\]\)\}]\s*", re.IGNORECASE) # check @ pattern sebab nak stop spam bot
DOT_PATTERN = re.compile(r"\s*[\[\(\{]\s*dot\s*[\]\)\}]\s*", re.IGNORECASE) # check . pattern sebab nak stop spam bot
FILE_ENDINGS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js") # elak ending file


def extract_emails(text):  # function 
    if not text:  
        return set()  

    soup = BeautifulSoup(text, "html.parser") 
    pieces = []  
    for link in soup.find_all("a", href=True): 
        href = link["href"]  
        if href.lower().startswith("mailto:"):  
            pieces.append(unquote(href[7:])) # check every clickable link, if it starts with mailto: dia akan take out the hidden email and save it

    pieces.append(soup.get_text(separator=" ")) # get all the text yang visitor nampak kat page, buang semua tag, and tukar &#64; jadi @

    all_text = " ".join(pieces)  

    all_text = AT_PATTERN.sub("@", all_text)  #  at jadi @
    all_text = DOT_PATTERN.sub(".", all_text)  # dot jadi .

    emails = set()  # set no dup
    for email in EMAIL_PATTERN.findall(all_text):  # email in text
        email = email.lower().strip(".") 
        if not email.endswith(FILE_ENDINGS):  # elak ending file 
            emails.add(email)  # save email 

    return emails  
