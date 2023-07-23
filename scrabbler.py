import math
import random
from collections import Counter
import more_itertools

class Player():
    def __init__(self, isBot):
        self.hand = Counter()
        self.score = 0
        self.isBot = isBot

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


class Scrabbler():
    def __init__(self):
        self.board = Board()
        self.players = []
    
    def addPlayer(self, player):
        self.players.append(player)

    def optimizeDictionary(self, inputFilename, outputFilename):
        with open(inputFilename, mode='r', encoding="utf-8") as input:
            with open(outputFilename, mode='w', encoding="utf-8") as output:
                initials = 'aa'
                lines = input.readlines()
                for word in lines:
                    if initials != word[0:2]:
                        initials = word[0:2]
                        print(initials)
                    if word.isalpha():
                        for spelling in self.spellings(word.lower()):
                            if self.isSubsetOf(spelling, self.bag) and len(spelling)<=15:
                                output.write(' '+' '.join(spelling)+' \n')

    def loadDictionary(self, filename):
            self.dictionary = set()
            self.spellingDictionary = []
            with open(filename, mode='r', encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    self.dictionary.add(''.join(line.split()))
                    self.spellingDictionary.append(line.split())
        
    def loadLetterCounts(self, filename):
        self.bag = Counter()
        with open(filename, mode='r', encoding="utf-8") as file:
            for line in file:
                (letter, count) = line.split()
                self.bag[letter] = int(count)
    
    def loadLetterPoints(self, filename):
        self.letterPoints = Counter()
        with open(filename, mode='r', encoding="utf-8") as file:
            for line in file:
                (letter, point) = line.split()
                self.letterPoints[letter] = int(point)
    
    def isWordInBag(self, word):
        return any(self.isSubsetOf(spelling, self.bag) for spelling in self.spellings(word))
    
    def areLettersInBag(self, letters):
        return Counter(letters) <= self.bag
    
    def wordProbability(self, word):
        probability = 0
        for spelling in self.spellings(word):
            if(self.areLettersInBag(spelling)):
                letters = Counter(spelling)
                probability += math.prod([math.comb(self.bag[letter],count) for letter, count in letters.items()]) / math.comb(self.bag.total(), letters.total())
        return probability
    
    def lettersProbability(self, letters, draws=6):
        probability = 0
        draws=max(draws, letters.total())
        if(self.areLettersInBag(letters)):
            letters = Counter(letters)
            p = math.prod([math.comb(self.bag[letter],count) for letter, count in letters.items()])
            if(draws>letters.total()):
                p *= math.comb(self.bag.total(), draws-letters.total())
            p /= math.comb(self.bag.total(), draws)
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

    def findValidWords(self, letterset, n=10):
        return sorted([word for word in self.spellingDictionary if Counter(word)<=letterset], key=self.baseValue, reverse=True)[:10]

    def baseValue(self, letters):
        value = sum([self.letterPoints[letter] for letter in letters])
        if len(letters)>=7:
            value += 50
        return value

    def dealLetter(self):
        letter = random.choice(list(self.bag.elements()))
        self.bag[letter] -= 1
        return letter
    
    def removeFromBag(self, letter):
        self.bag[letter] -= 1
        return letter
    
    def spellings(self, word):
        return [[''.join(block) for block in spelling] for spelling in more_itertools.partitions(word) if all(''.join(block) in self.bag for block in spelling)]
    
    def missingLetters(have, need):
        return Counter(need)-Counter(have)

    def findPossibleWords(self, letterset, length, n=10):
        words = [(word, requiredLetters) for word,requiredLetters in self.spellingDictionary if requiredLetters.total()>=length]
        return sorted(words, key=lambda w:self.lettersProbability(w[1] - letterset, length), reverse=True)[:n]



#end of class

s = Scrabbler()

#s.optimizeDictionary("dictionary_HUN.txt", "dictionary_scrabble_HUN.txt")
s.loadDictionary("dictionary_scrabble_HUN.txt")
s.loadLetterCounts("letter_counts_HUN.txt")
s.loadLetterPoints("letter_points_HUN.txt")

s.board.draw()
s.addPlayer(Player(True))
for player in s.players:
    for i in range(7):
        player.hand[s.dealLetter()] += 1

for player in s.players:
    if player.isBot:
        print(player.hand)
        #for word in s.findValidWords(player.hand):
        #   print(s.baseValue(word),' - ',word)
        word = s.findValidWords(player.hand,1)[0]
        print(word)
        length = len(word)
        s.board.playWord(7-length//2,7,'horizontal', word)
        player.score += s.wordPoints(word)

s.board.draw()

#print(s.dictionary[0])
#print(s.spellings("madzszar"))

#for length in range(2,10):
#    print(s.top(length))

#for word in s.findValidWords(Counter("a s sz e é r h".split())):
#    print(s.baseValue(word),' - ',word)


#hand=Counter("ny e r s k s t".split())
#for letter in hand:
#    for i in range(hand[letter]):
#        s.removeFromBag(letter)

#print(hand)


#for word, requiredLetters in s.findPossibleWords(hand, 7, 10):
#    print(s.baseValue(word),' - ',word,' - ',requiredLetters-hand,' - ',s.lettersProbability(requiredLetters-hand))

#word = "kenyeres"
#requiredLetters = Counter("k e ny e r e s".split())
#print(s.baseValue(word),' - ',word,' - ',requiredLetters-hand,' - ',s.lettersProbability(requiredLetters-hand))


#[word for word,requiredLetters in s.spellingDictionary if requiredLetters.total()==2]
