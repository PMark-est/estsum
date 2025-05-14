class Score:
    def __init__(self):
        self.word_count_in_sentence = 0
        self.position_score = 0
        self.frequency_score = 0
        self.format_score = 0
        self.meaning_score = 1
        self.total_score = 0
    
    def calculate_total_score(self, POSITION_SCORE_WEIGHT, FORMAT_SCORE_WEIGHT, FREQUENCY_SCORE_WEIGHT):
        self.total_score = self.meaning_score * (POSITION_SCORE_WEIGHT * self.position_score + FORMAT_SCORE_WEIGHT * self.format_score + FREQUENCY_SCORE_WEIGHT * self.frequency_score)

