import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional, List
from estnltk import Text
from estnltk.taggers import SentenceTokenizer
import string

class HTMLMuundur:
    """
    A class that fetches HTML from a given URL and converts it into a structured,
    XML-like format with headers, paragraphs, and sentences marked up with custom tags.
    It specifically extracts content from the <article> or <main> tags.
    """

    def __init__(self, url: Optional[str] = None) -> None:
        """
        Initialize the converter with a URL. Optionally provide a URL to parse right away.

        Args:
            url (str, optional): The URL of the HTML page to be converted.
        """
        self.url: Optional[str] = url
        self.soup: Optional[BeautifulSoup] = None
        self.output = None

        if url:
            self.parse_url(url)

    def fetch_html(self, url: str) -> None:
        """
        Fetches and parses the HTML content from the specified URL.
        Raises an exception if the request fails.

        Args:
            url (str): The URL to fetch HTML from.
        """
        response = requests.get(url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def extract_main_content(self) -> Tag:
        """
        Extracts the main content from the <article> or <main> tag.
        If neither is found, raises an error.

        Returns:
            Tag: The extracted <article> or <main> tag.
        """
        if not self.soup:
            raise ValueError("Soup not initialized.")
        article_tag = self.soup.find(['article', 'main'])
        if not article_tag:
            raise ValueError("No <article> or <main> tag found in the page.")
        return article_tag

    def extract_main_title(self) -> None:
        """
        Extracts the main title from the first <h1> tag and writes it to the output.

        Args:
            article_tag (Tag): The article or main container tag.
        """
        h1 = self.soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
            self.output.write(f'<head><hi rend="bold">{title}</hi></head>')

    
    def process(self):
        main_content: Tag = self.extract_main_content()
        paragraphs = main_content.find_all('p')
        i = 0
        for paragraph in paragraphs:
            self.output.write(f"<p>\n")    
            i += 1
            text = Text(paragraph.text).tag_layer(['words'])
            SentenceTokenizer().tag(text)
            for sent in text['sentences']:
                sentence = self.join_words_with_punctuation(sent.text)
                self.output.write(f"<s>{sentence}</s>\n") 
            self.output.write(f"</p>\n")    
            

    def join_words_with_punctuation(self, words):
        puncuation = '“!"#$%&\'*+,-./:;<=>?@^_`|~)}]\\'
        result = []
        last_word = ""
        for i, word in enumerate(words):
            # If the word ends with punctuation, no space before it
            if word[-1] in puncuation:
                if result:
                    result[-1] += word  # Merge with the last word
                else:
                    result.append(word)  # Just in case the first word is punctuation
            elif last_word in "„({[":
                result.append(word) # For if the last character was an opening bracket so we dont have random whitespace
            else:
                if result:
                    result.append(" " + word)  # Add a space before regular words
                else:
                    result.append(word)  # No space before the first word
            last_word = word

        return ''.join(result)


    def parse_url(self, url: str, filename: str) -> None:
        """
        Parses a given URL and writes the structured output to a file.

        Args:
            url (str): The URL of the HTML page.
            filename (str): The path to the output file.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            self.output = f
            self.output.write("<div0>")
            self.fetch_html(url)

            self.extract_main_title()
            self.process()

            self.output.write("<div0>")