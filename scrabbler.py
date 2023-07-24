import math
import random
from collections import Counter
import more_itertools
import os

class Player():
    def __init__(self, isBot):
        self.hand = Counter()
        self.score = 0
        self.isBot = isBot
    
    def startingMove(self):
        word = s.findValidWords(self.hand,1)[0]
        for letter in word:
            self.hand[letter] -= 1
        #print(word)
        direction = 'horizontal'
        x = 7-len(word)//2
        y = 7
        return x, y, direction, word

class Board():
    def __init__(self):
        self.board = [['' for j in range(15)] for i in range(15)]
    
    def draw(self):
        for y in range(15):
            print(''.join(['['+self.board[y][x]+' '*(2-len(self.board[y][x]))+']' for x in range(15)]))
    
    def playWord(self, x, y, dir, word):
        if dir=='horizontal':
            for i in range(len(word)):
                self.board[y][x+i]=word[i]
        else:
            if dir=='vertical':
                for i in range(len(word)):
                    self.board[y+i][x]=word[i]

class Bag:
    def __init__(self):
        self.letters = Counter()
    
    def loadLetterCounts(self, filename):
        self.validLetters = []
        self.letters = Counter()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, filename), mode='r', encoding="utf-8") as file:
            for line in file:
                (letter, count) = line.split()
                self.letters[letter] = int(count)
                if int(count)>0:
                    self.validLetters.append(letter)
    
    def areLettersIn(self, letters):
        return Counter(letters) <= self.letters

    def draw(self, n=1):
        letters = Counter()
        for i in range(n):
            letter = random.choice(list(self.letters.elements()))
            letters[letter] += 1
            self.letters[letter] -= 1
        return letters
    
    def remove(self, letter):
        self.letters[letter] -= 1
        return letter

class Scrabbler():
    def __init__(self):
        self.board = Board()
        self.bag = Bag()
        self.bag.loadLetterCounts('letter_counts_HUN.txt')
        self.players = []
        while True:
            try:
                self.loadDictionary("dictionary_scrabble_HUN.txt")
            except:
                self.optimizeDictionary("dictionary_HUN.txt", "dictionary_scrabble_HUN.txt")
                continue
            break

        self.loadLetterPoints("letter_points_HUN.txt")
    
    def addPlayer(self, player):
        self.players.append(player)

    def optimizeDictionary(self, inputFilename, outputFilename):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, inputFilename), mode='r', encoding="utf-8") as input:
            with open(os.path.join(__location__, outputFilename), mode='w', encoding="utf-8") as output:
                initials = 'aa'
                lines = input.readlines()
                for word in lines:
                    word = word.rstrip('\n')
                    if initials != word[0:2]:
                        initials = word[0:2]
                        print(initials)
                    if word.isalpha():
                        for spelling in self.spellings(word.lower()):
                            if self.isSubsetOf(spelling, self.bag.letters) and len(spelling)<=15:
                                output.write(' '+' '.join(spelling)+' \n')

    def loadDictionary(self, filename):
        self.dictionary = set()
        self.spellingDictionary = []
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, filename), mode='r', encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.dictionary.add(''.join(line.split()))
                self.spellingDictionary.append(line.split())
    
    def loadLetterPoints(self, filename):
        self.letterPoints = Counter()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, filename), mode='r', encoding="utf-8") as file:
            for line in file:
                (letter, point) = line.split()
                self.letterPoints[letter] = int(point)
    
    def wordProbability(self, word):
        if len(word)==0:
            return 0
        probability = 0
        for spelling in self.spellings(word):
            if not self.bag.areLettersIn(spelling):
                next
            letters = Counter(spelling)
            p = math.prod([math.comb(self.bag.letters[letter],count) for letter, count in letters.items()]) / math.comb(self.bag.letters.total(), letters.total())
            probability += p
        return probability
    
    def lettersProbability(self, letters, draws=6):
        probability = 0
        draws=max(draws, letters.total())
        if(self.bag.areLettersIn(letters)):
            letters = Counter(letters)
            p = math.prod([math.comb(self.bag.letters[letter],count) for letter, count in letters.items()])
            if(draws>letters.total()):
                p *= math.comb(self.bag.letters.total(), draws-letters.total())
            p /= math.comb(self.bag.letters.total(), draws)
            probability += p
        return probability

    def top(self, length, n=10):
        return sorted([word for word in self.dictionary if len(word) == length], key=lambda word:(self.wordProbability(word)), reverse=True)[:n]

    @staticmethod
    def isAnagram(word1, word2):
        return Counter(word1) == Counter(word2)
    
    @staticmethod
    def isSubsetOf(word1, word2):
        return Counter(word1) <= Counter(word2)
    
    @staticmethod
    def maxLength(letters):
        return sum([len(letter)*count for letter, count in letters.items()])

    def findValidWords(self, letterset, n=10):
        return sorted([word for word in self.spellingDictionary if Counter(word)<=letterset], key=self.wordPoints, reverse=True)[:10]

    def wordPoints(self, letters):
        return sum([self.letterPoints[letter] for letter in letters]) + 50*(len(letters) >= 7)
    
    def spellings(self, word):
        return [[''.join(block) for block in spelling] for spelling in more_itertools.partitions(word) if all(''.join(block) in self.bag.letters for block in spelling)]
    
    @staticmethod
    def missingLetters(have, need):
        return Counter(need) - Counter(have)

    def findPossibleWords(self, letterset, length=2, maxDifference=2):
        words = [word for word in self.spellingDictionary if len(word)>=length and self.missingLetters(letterset, word).total()<=maxDifference]
        return sorted(words, key=lambda word:self.lettersProbability(self.missingLetters(letterset, word), length), reverse=True)

    def playWord(self, player, move):
        x, y, direction, word = move
        self.board.playWord(x, y, direction, word)
        player.score += self.wordPoints(word)
        player.hand += self.bag.draw(len(word))


#end of class

random.seed(0)

s = Scrabbler()

s.addPlayer(Player(True))
for player in s.players:

    #Set hand manually:
    #player.hand=Counter("ny e r s k s t".split())
    #for letter in player.hand:
    #    for i in range(player.hand[letter]):
    #        s.bag.remove(letter)

    player.hand += s.bag.draw(7)

player = random.choice(s.players)
if player.isBot:
    print("Starting hand:")
    print(player.hand)
    print("Highest scoring valid words:")
    for word in s.findValidWords(player.hand):
        print(s.wordPoints(word),' - ',word)
    print("Highest chance to ace with following words (max 2 difference):")   
    for word in s.findPossibleWords(player.hand, 7, 2):
        print(s.wordPoints(word),' - ',word,' - ',s.missingLetters(player.hand, word),' - ',s.lettersProbability(s.missingLetters(player.hand, word)))
    print("Chance to play specific word with specific spelling (k e ny e r e s):")
    word = "k e ny e r e s".split()
    print(s.wordPoints(word),' - ',word,' - ',s.missingLetters(player.hand, word),' - ',s.lettersProbability(s.missingLetters(player.hand, word)))


    s.playWord(player, player.startingMove())
print("Board after starting move:")
s.board.draw()
print("New hand:")
print(player.hand)

print("Top 10 most probable words for each length")
for length in range(2,10):
    print(s.top(length))