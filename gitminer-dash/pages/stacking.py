def is_disjoint(seq1, seq2):
    return seq1[0] > seq2[1] or seq2[0] > seq1[1]


class SequenceStacker:
    def __init__(self):
        self.past_sequences = []

    def height_for(self, sequence):
        hits = [1 for old_sequence in self.past_sequences
                if not is_disjoint(sequence, old_sequence)]
        elevation = sum(hits) + 1
        self.past_sequences.append(sequence)
        return elevation
