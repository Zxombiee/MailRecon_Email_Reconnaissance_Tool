from urllib.parse import urldefrag, urljoin, urlparse  # untuk handle URL
from urllib.robotparser import RobotFileParser  # untuk baca robots.txt

from bs4 import BeautifulSoup

from . import safety  # scope 
from .http import USER_AGENT  # user agent tool

#variable
SKIP_FILES = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".exe", ".mp4", ".css", ".js") # elak file
REDIRECT_CODES = (301, 302, 303, 307, 308) # status code 


def find_links(page_url, html_text):  # function cari semua link dalam satu page
    soup = BeautifulSoup(html_text, "html.parser")  # baca HTML page
    links = []  # list untuk simpan link
    for tag in soup.find_all("a", href=True):  # check every clickable link kat page
        full_url = urljoin(page_url, tag["href"])  # tukar link pendek jadi penuh, contoh /team.html jadi http://site/team.html
        full_url = urldefrag(full_url)[0]  # buang #section, sebab page.html#top sama je dengan page.html
        if not full_url.startswith(("http://", "https://")):  # if not web link skip
            continue
        if full_url.lower().endswith(SKIP_FILES):  # if file skip
            continue
        links.append(full_url)  # save link
    return links  # state link apa ada


def load_robots(start_url, fetcher):  # function baca robots.txt, rules dari website owner
    site = urlparse(start_url)  # pecahkan URL jadi bahagian (http, 127.0.0.1:8080, ...)
    robots = RobotFileParser()  # Python punya robots.txt reader
    response = fetcher.get(f"{site.scheme}://{site.netloc}/robots.txt")  # download robots.txt guna fetcher 
    if response.status_code == 200:  # kalau robots.txt ada
        robots.parse(response.text.splitlines())  # baca rules line by line
    else:
        robots.parse([])  # takde robots.txt = takde rules, semua boleh visit
    return robots  # bagi balik robots reader


def crawl(start_url, fetcher, max_pages):  # main function crawler
    if urlparse(start_url).path == "":  # check path kalau kosong 
        start_url += "/"  # tambah / sebab http://site sama dengan http://site/

    robots = load_robots(start_url, fetcher)  # baca robots.txt dulu sebelum crawl
    queue = [start_url]  # list page yang tunggu nak visit
    visited = set()  # page yang dah visit, supaya tak visit 2 kali
    pages = 0  # kira berapa page dah collect

    while queue and pages < max_pages:  # loop till max page
        url = queue.pop(0)  # first page queue
        if url in visited:  # if visit, skip
            continue
        visited.add(url)  # alreadt visit

        if not robots.can_fetch(USER_AGENT, url):  # check robots.txt, boleh visit tak
            print(f"    [skip] {url} (blocked by robots.txt)")  # tak boleh, skip
            continue

        try:
            response = fetcher.get(url)  # download page guna fetcher http.py
        except safety.OutOfScope as error:  # banyak sangat request stop (limit http.py plus 1 max page)
            print(f"    [stop] {error}")  # stop crawl
            return

        if response.status_code in REDIRECT_CODES:  # redirect page
            new_url = urljoin(url, response.headers.get("Location", ""))  # ambil address baru
            if fetcher.allowed(new_url):  # kalau address baru dalam scope
                queue.insert(0, new_url)  # letak depan queue lestu nanti dia visit
            continue

        if response.status_code != 200 or "html" not in response.headers.get("Content-Type", ""):  # error or not HTML dia skip
            continue  

        pages += 1  
        yield url, response.text 

        for link in find_links(url, response.text):  # cari link dalam page 
            if link in visited:  # dah visit, skip
                continue
            if fetcher.allowed(link):  # kalau link dalam scope
                queue.append(link)  # queue nanti visit
            elif link not in fetcher.blocked:  # kalau luar scope save
                fetcher.blocked.append(link)  # save in report
