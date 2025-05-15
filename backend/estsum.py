"""EstSum Implementation"""

import re
import time
from collections import defaultdict
from bs4 import BeautifulSoup
from bs4.element import Tag
from estnltk import Text
from Score import Score
from groq import Groq

API_KEY = "api võti"

class EstSum:
    """
    An extractive text summarizer for the estonian language
    """

    def __init__(self):
        """
        Initializes the EstSum class with necessary attributes.
        """
        self.title = None
        self.article_word_count = 0
        self.sentence_position = 0
        self.absolute_sentence_position_score_weights = {1: 20, 2: 5}
        self.sentence_position_score_weights = {
            "article": {1: 5, 2: 2, 3: 1}, "sub_chapter": {2: 5}}
        self.format_pattern_weights = {
            '[?!]+$': -5, '[„“«»"]': -4, '[!?]+\"': -13, '^\xAB[^\xBB]*,\xBB': -4, ': \xAB[^\xBB]*\xBB$': -4, '^\xAB[^\xBB]*\xBB$': -4}
        self.scores = defaultdict(Score)
        self.words = defaultdict(int)
        #self.client = Groq(
        #    api_key=API_KEY,
        #)
        self.summary = []
        #self.position_score_weight = 0.4
        #self.format_score_weiht = 0.4
        #self.frequency_score_weight = 0.2
        #self.compression_rate = 0.3

    def reset_variables(self):
        self.title = None
        self.article_word_count = 0
        self.sentence_position = 0
        self.scores = defaultdict(Score)
        self.words = defaultdict(int)
        self.summary = []

    def process_sub_chapter(self, sub_chapter: Tag):
        """
        Processes a sub-chapter by iterating through its lines and processing each paragraph.

        :param sub_chapter: BeautifulSoup Tag representing the sub-chapter.
        """
        for line in sub_chapter:
            if line == '\n' or line.name == "head":
                continue
            self.process_paragraph(line, in_subchapter=True)

    def calculate_position_score(self, score: Score, position: int, weight_type: str):
        """
        Calculates the position score for a sentence based on its position and weight type.

        :param score: Score object to store the calculated score.
        :param position: Position of the sentence in the paragraph or sub-chapter.
        :param weight_type: Type of weight to apply ("article" or "sub_chapter").
        """
        self.sentence_position += 1

        score.position_score += self.absolute_sentence_position_score_weights.get(
            self.sentence_position, 0)

        score.position_score += self.sentence_position_score_weights[weight_type].get(
            position, 0)

    def calculate_format_score(self, score: Score, sentence: Tag):
        """
        Calculates the format score for a sentence based on its text format.

        :param score: Score object to store the calculated score.
        :param sentence: BeautifulSoup Tag representing the sentence.
        """
        score.format_score = 5
        if sentence.hi:
            score.format_score += 8
            sentence = sentence.hi
            if re.search("[!?]+$", sentence.getText()):
                score.format_score -= 13

        sentence = sentence.getText()

        for pattern, pattern_score in self.format_pattern_weights.items():
            if re.search(pattern, sentence):
                score.format_score += pattern_score

    def calculate_frequency_score(self):
        """
        Calculates the frequency score for each sentence based on word frequencies.
        """
        for sentence, score in self.scores.items():
            sentence_without_punctuation = Text(
                re.sub("[-,.!?;:\xAB\xBB\"()„’́'“«»]+", " ", sentence)).tag_layer()

            lemmas = sentence_without_punctuation.words.lemma
            score.word_count_in_sentence = len(lemmas)

            for lemma in lemmas:
                score.frequency_score += self.words[lemma[0].lower()]

    def calculate_meaning_score(self):
        sentences = self.scores.keys()
        scores = self.scores.values()

        batched_sentences = "\n".join(
            f"{i+1}. nr{sentence}" for i, sentence in enumerate(sentences))
        print(self.title.text)
        role = f""" 
        Te olete sisukokkuvõtja. Teile on antud nimekiri lausetest pikemast tekstist ning üks pealkiri või põhiteema kujul: "{self.title.text}". Teie ülesanne on hinnata iga lause olulisust, otsustamaks, kas see tuleks kaasata kokkuvõttesse.
        Arvesta iga lause informatiivset väärtust, mitte ainult sarnasust pealkirjaga. Hinda, kas lause aitab edasi anda teema põhisisu, lisab olulisi detaile või selgitusi.
        Iga lause kohta anna hinnang skaalal 0.0 kuni 1.0 järgmiselt:
        1.0 -- Väga oluline, keskse sisuga lause
        0.5 - 0.9 -- Tähtis või täiendav, toetab põhisisu
        0.1 - 0.4 -- Vähem tähtis, aga teemaga seotud
        0.0 -- Ebaoluline või teemast kõrvalekalduv
        Tagasta hinnangute loetelu uuel real igale sisendlausele, täpselt samas järjekorras. Vorming peab olema järgmine:
        "
        0.2
        0.3
        0.7
        1.0
        ...
        "
"""

        prompt = [{"role": "system",
                   "content": role},

                  {"role": "user",
                   "content": batched_sentences}]
        chat_completion = self.client.chat.completions.create(
            messages=prompt,
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
        )

        semantic_scores = [float(line.replace(
            ',', '.')) for line in chat_completion.choices[0].message.content.splitlines()]
        print(semantic_scores)

        for i, score in enumerate(scores):
            score.meaning_score = semantic_scores[i]

    def count_word_frequencies(self, sentence: str):
        """
        Counts word frequencies in a sentence and updates the article word count.

        :param sentence: BeautifulSoup Tag representing the sentence.
        """
        sentence_without_punctuation = Text(
            re.sub("[-,.!?;:\xAB\xBB\"()„’́'“«»]+", " ", sentence)).tag_layer()

        self.article_word_count += len(sentence_without_punctuation.words)
        lemmas = sentence_without_punctuation.words.lemma

        for lemma in lemmas:
            self.words[lemma[0].lower()] += 1

    def process_paragraph(self, paragraph: Tag, in_subchapter: bool):
        """
        Processes a paragraph by iterating through its sentences and calculating scores.

        :param paragraph: BeautifulSoup Tag representing the paragraph.
        :param in_subchapter: Boolean indicating if the paragraph is in a sub-chapter.
        """
        sentence_position = 0
        weight_type = "article" if not in_subchapter else "sub_chapter"

        for sentence in paragraph:
            if sentence == '\n':
                continue
            sentence_position += 1

            score = Score()
            self.scores[sentence.getText()] = score

            self.calculate_position_score(
                score, sentence_position, weight_type)
            self.calculate_format_score(score, sentence)

            sentence = sentence.getText()

            self.count_word_frequencies(sentence)

    def print_sentences(self, output_name: str, write_to_file: bool, compression_rate: float):
        """
        Prints the sentences to an output file based on their scores.
        """
        summary_length = int(compression_rate * self.article_word_count)
        threshold = self.calculate_min_score(summary_length)
        with open(output_name, 'w', encoding="utf-8") as wf:
            for sentence, score in self.scores.items():
                if score.total_score < threshold:
                    continue
                if write_to_file:
                    wf.write(sentence + "\n")
                else:
                    self.summary.append(sentence)

    def calculate_min_score(self, summary_length: int) -> int:
        """
        Calculates the minimum score required for a sentence to be included in the summary.

        :param summary_length: Length of the summary in terms of word count.
        :return: Minimum score threshold.
        """
        summary_length -= len(self.title.words) - 10

        if summary_length < 0:
            return 10_000

        scores = sorted(
            ((score.total_score, score.word_count_in_sentence)
             for score in self.scores.values()),
            reverse=True
        )

        min_mum = 10_000
        for score, word_count in scores:
            if word_count < summary_length:
                min_mum = score
                summary_length -= word_count
            else:
                break

        return min_mum

    def normalize_scores(self):
        """
        Normalizes the scores of all sentences.
        """
        position_score = sum(
            score.position_score for score in self.scores.values())
        frequency_score = sum(
            score.frequency_score for score in self.scores.values())
        format_score = sum(
            score.format_score for score in self.scores.values())

        if format_score == 0:
            format_score = 1

        if frequency_score == 0:
            frequency_score = 1

        for score in self.scores.values():
            score.position_score = round(
                score.position_score * 100 / position_score, 6)
            score.frequency_score = round(
                score.frequency_score * 100 / frequency_score, 6)
            score.format_score = round(
                score.format_score * 100 / format_score, 6)

    def normalize_word_weights(self):
        """
        Normalizes the word weights based on frequency and stop words.
        """
        with open('lemmasagedused.txt', encoding="utf-8") as f:
            frequent_lemmas = {lemma.strip().lower(): float(frequency)
                               for lemma, frequency in (line.split("\t") for line in f)}

        with open('stoppsonad.txt', encoding="utf-8") as f:
            stop_words = {line.strip().lower() for line in f}

        x = 10_000 / self.article_word_count

        for word in self.words:
            if word in stop_words:
                self.words[word] = 0
                continue
            if re.search("\\s+", word):
                self.words[word] = 0
                continue
            self.words[word] = round(self.words[word] * x, 2)
            if word in frequent_lemmas:
                self.words[word] = max(
                    0, self.words[word] - frequent_lemmas.get(word, 0))
    
    def get_coverage(self, original_summary: str, generated_summary: str):
        """
        Calculates the coverage percentage between the two files.

        :param original_summary: Path to the file that contains the labeled summary.
        :param generated_summary: Path to the file that contains the generated summary.
        """
        with open(original_summary, 'r') as read_file:
            original_summary_lines = read_file.readlines()

        with open(generated_summary, 'r') as read_file:
            generated_summary_lines = read_file.readlines()


        hits = 0
        
        for generated_summary_line in generated_summary_lines:
            for original_summary_line in original_summary_lines:
                if generated_summary_line[0] != original_summary_line[0]:
                    continue
                
                if generated_summary_line.strip() != original_summary_line.strip():
                    continue
                
                hits += 1
        
        return hits / len(generated_summary_lines)



    def summarize(self, file: str, output: str, write_to_file: bool, alpha: float, beta: float, gamma:float, length: float):
        """
        Summarizes the given file by processing its content and generating a summary.

        :param file: Path to the input file.
        """
        #start_time = time.time()
        with open(file, encoding="utf-8-sig") as input_file:
            soup = BeautifulSoup(input_file.read(), "html.parser")
            soup.div0.unwrap()  # Remove the div0 wrapper
            self.title = Text(soup.head.extract().getText()).tag_layer()

            for line in soup:
                if line == '\n':
                    continue
                tag_name = line.name

                if tag_name == 'p':
                    self.process_paragraph(line, in_subchapter=False)
                elif tag_name == "div":
                    self.process_sub_chapter(line)

            self.calculate_frequency_score()
            self.normalize_scores()

            #self.calculate_meaning_score()

            for score in self.scores.values():
                score.calculate_total_score(
                    alpha, beta, gamma)

            self.print_sentences(output, write_to_file, length)

        #print(time.time() - start_time)
