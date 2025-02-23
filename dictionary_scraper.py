import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import logging
import trafilatura

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DictionaryScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_mbti_info(self, word: str) -> Optional[Dict]:
        """
        Get MBTI personality type information
        """
        mbti_types = {
            'INTJ': ('Architect', 'Introverted, Intuitive, Thinking, Judging'),
            'INTP': ('Logician', 'Introverted, Intuitive, Thinking, Perceiving'),
            'ENTJ': ('Commander', 'Extroverted, Intuitive, Thinking, Judging'),
            'ENTP': ('Debater', 'Extroverted, Intuitive, Thinking, Perceiving'),
            'INFJ': ('Advocate', 'Introverted, Intuitive, Feeling, Judging'),
            'INFP': ('Mediator', 'Introverted, Intuitive, Feeling, Perceiving'),
            'ENFJ': ('Protagonist', 'Extroverted, Intuitive, Feeling, Judging'),
            'ENFP': ('Campaigner', 'Extroverted, Intuitive, Feeling, Perceiving'),
            'ISTJ': ('Logistician', 'Introverted, Sensing, Thinking, Judging'),
            'ISFJ': ('Defender', 'Introverted, Sensing, Feeling, Judging'),
            'ESTJ': ('Executive', 'Extroverted, Sensing, Thinking, Judging'),
            'ESFJ': ('Consul', 'Extroverted, Sensing, Feeling, Judging'),
            'ISTP': ('Virtuoso', 'Introverted, Sensing, Thinking, Perceiving'),
            'ISFP': ('Adventurer', 'Introverted, Sensing, Feeling, Perceiving'),
            'ESTP': ('Entrepreneur', 'Extroverted, Sensing, Thinking, Perceiving'),
            'ESFP': ('Entertainer', 'Extroverted, Sensing, Feeling, Perceiving')
        }

        word_upper = word.upper()
        if word_upper in mbti_types:
            nickname, traits = mbti_types[word_upper]
            return {
                'definitions': [
                    f"MBTI Personality Type: {word_upper} - Known as '{nickname}'",
                    f"Stands for: {traits}",
                    "Part of the Myers-Briggs Type Indicator (MBTI), a personality type system based on Carl Jung's theory of psychological types."
                ],
                'examples': [
                    f"As an {word_upper}, they excel at analytical problem-solving and strategic thinking.",
                    f"The {word_upper} personality type is often found in careers that match their {nickname.lower()} traits."
                ],
                'etymology': "The Myers-Briggs Type Indicator (MBTI) was developed by Isabel Myers and her mother Katherine Briggs based on Carl Jung's theory of personality types.",
                'usage_notes': [
                    "MBTI types should not be used to discriminate or stereotype individuals, as personality is complex and can vary based on context and personal growth.",
                    "While MBTI is widely used in personal development and career counseling, it is important to note that it is just one of many personality assessment tools."
                ]
            }
        return None

    def get_word_info(self, word: str) -> Optional[Dict]:
        """
        Scrapes dictionary.com for word information
        Returns a dictionary containing definitions, examples, and etymology
        """
        # First check if it's an MBTI type
        mbti_info = self._get_mbti_info(word)
        if mbti_info:
            logger.info(f"Found MBTI information for: {word}")
            return mbti_info

        try:
            url = f"https://www.dictionary.com/browse/{word.lower().strip()}"
            logger.info(f"Fetching definition for word: {word}")

            # First try with trafilatura to get the main content
            downloaded = trafilatura.fetch_url(url)
            main_content = trafilatura.extract(downloaded)

            if not main_content:
                logger.warning(f"No content found for word: {word}")
                return None

            # Now use requests + BeautifulSoup for structured data
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get all definition sections
            definitions = []
            definition_sections = soup.select('div[data-type="word-definitions"] .e1q3nk1v3')

            for section in definition_sections:
                # Get part of speech
                pos = section.select_one('.luna-pos')
                pos_text = pos.text.strip() if pos else ''

                # Get definitions from this section
                def_elements = section.select('.e1q3nk1v4')
                for def_elem in def_elements:
                    if def_elem.text.strip():
                        # Include part of speech with definition
                        full_def = f"({pos_text}) {def_elem.text.strip()}" if pos_text else def_elem.text.strip()
                        definitions.append(full_def)

            # Get examples
            examples = []
            example_elements = soup.select('.e1q3nk1v6')
            for example in example_elements:
                text = example.text.strip()
                if text and word.lower() in text.lower():
                    examples.append(text)

            # Get etymology from main content
            etymology = ""
            etym_element = soup.select_one('.e1cc33ff0')
            if etym_element:
                etymology = etym_element.text.strip()

            # Get additional notes (slang, medical, etc.)
            usage_notes = []
            note_elements = soup.select('.e1ninw8k0')
            for note in note_elements:
                if note.text.strip():
                    usage_notes.append(note.text.strip())

            # If no definitions found in structured data, try to extract from main content
            if not definitions and main_content:
                content_lines = main_content.split('\n')
                for line in content_lines:
                    line = line.strip()
                    if line and len(line) > 20 and not line.startswith('Example'):
                        definitions.append(line)
                definitions = definitions[:5]  # Limit to top 5 definitions

            if not definitions:
                logger.warning(f"No definitions found for word: {word}")
                return None

            logger.info(f"Successfully retrieved information for word: {word}")
            return {
                'definitions': definitions[:5],  # Limit to top 5 definitions
                'examples': examples[:3],  # Limit to top 3 examples
                'etymology': etymology,
                'usage_notes': usage_notes[:2]  # Limit to top 2 usage notes
            }

        except requests.RequestException as e:
            logger.error(f"Error fetching word '{word}': {str(e)}")
            return None
        finally:
            time.sleep(1)  # Rate limiting