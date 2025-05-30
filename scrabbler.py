import math
import random
from collections import Counter
import more_itertools
import os
import re
import time

class Player():
    """Class for keeping track of all information related to a single player, bot or human.

    Attributes:
        hand: Counter class keeping track of letters available in hand.
        score: Integer value keeping track of the current score.
        isBot: Boolean indicating if the player is a bot or not.
    """

    def __init__(self, isBot):
        """Initializes Player class.

        Args:
            isBot: A boolean indicating if the player is a bot or not.
        """
        self.hand = Counter()
        self.score = 0
        self.isBot = isBot
    
    def startingMove(self):
        """Returns the starting coordinates, direction and the letters of the biggest scoring word that can be played, assuming an empty board."""

        word = s.findValidWords(self.hand)[0]
        for letter in word:
            self.hand[letter] -= 1
        #print(word)
        direction = 'horizontal'
        x = 7-len(word)//2
        y = 7
        return x, y, direction, word

class Board():
    """Class for keeping track of board status.

    Attributes:
        board: 2D list of letters showing current board state.
    """
    def __init__(self):
        """Initializes Board class."""
        self.board = [['' for j in range(15)] for i in range(15)]
    
    def draw(self):
        """Draws board into the active terminal"""
        for y in range(15):
            print(''.join(['['+self.board[y][x]+' '*(2-len(self.board[y][x]))+']' for x in range(15)]))
    
    def playWord(self, x, y, direction, word):
        """Lays letters of a new word onto the board starting at given position.
        
        Args:
            x, y: Integer coordinates of the starting letter.
            direction: String indicating word direction. Valid values are 'horizontal' or 'vertical'.
            word: List of letters for the word to be played.
        """
        if direction=='horizontal':
            for i in range(len(word)):
                self.board[y][x+i]=word[i]
        else:
            if direction=='vertical':
                for i in range(len(word)):
                    self.board[y+i][x]=word[i]

class Bag:
    """Class for keeping track of a bag of letter tiles.

    Attributes:
        letters: Counter class keeping track of letters in bag.
        validLetters: List of strings containing every letter that appears on at least one tile.
    """
    def __init__(self):
        """Initializes Bag class."""
        self.letters = Counter()
    
    def loadLetterCounts(self, filename):
        """Resets bag based on input files content.
        
        Args:
            filename: String of the filename. File is assumed to be in the same directory as this .py runnable.
            direction: String indicating word direction. Valid values are 'horizontal' or 'vertical'.
            word: List of letters for the word to be played.
        """
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
        """Checks if a set of letters are in the bag currently.
        
        Args:
            letters: Iterable containing letters. Converted to Counter type to perform check.
        """
        return Counter(letters) <= self.letters

    def draw(self, n=1):
        """Draws random letter(s) from the bag. Removes letter(s) after draw.
        
        Args:
            n=1: Number of letters to draw. Defaults to 1.
        """
        letters = Counter()
        for i in range(n):
            letter = random.choice(list(self.letters.elements()))
            letters[letter] += 1
            self.letters[letter] -= 1
        return letters
    
    def remove(self, letter, n=1):
        """Removes letter(s) from the bag.
        
        Args:
            letter: String of letter to remove.
            n=1: Number of letters to remove. Defaults to 1.
        """
        try:
            self.letters[letter] -= 1
        except:
            return 0
        return n

class Dictionary():
    """Class for managing dictionary of valid words and relevant lookups.

    Attributes:
        dictionary: Set of strings containing valid words.
        regexDictionary: List of strings containing valid words with all valid spellings. Letters are separated by spaces.
        spellingDictionary: 
    """
    def __init__(self):
        """Initializes Dictionary class loading "dictionary_scrabble_HUN.txt". If this doest exist, it will be created based on "dictionary_HUN.txt"."""
        while True:
            try:
                self.loadDictionary("dictionary_scrabble_HUN.txt")
            except:
                self.optimizeDictionary("dictionary_HUN.txt", "dictionary_scrabble_HUN.txt")
                continue
            break
    
    @staticmethod
    def optimizeDictionary(self, inputFilename, outputFilename):
        """Converts a regular dictionary file into special scrabble dictionary, which containts every valid tile combination (spelling) for every word.

        Attributes:
            inputFilename: String filename of the regular directory. File is assumed to be in the same directory as this .py runnable.
            outputFilename: String filename of the optimized directory that will be created. File will be created in the same directory as this .py runnable.
        """
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
        """Loads an already optimized scrabble dictionary, which containts every valid tile combination (spelling) for every word.

        Attributes:
            filename: String of the filename. File is assumed to be in the same directory as this .py runnable.
        """
        self.dictionary = set()
        self.regexDictionary = []
        self.spellingDictionary = []
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, filename), mode='r', encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.dictionary.add(''.join(line.split()))
                self.regexDictionary.append(line.rstrip('\n'))
                self.spellingDictionary.append(line.split())

class Scrabbler():
    """Class for keeping track of a game a scrabble.

    Attributes:
        board: Board class for keeping track of board status.
        bag: Bag class for keeping track of bag of letters.
        players: List of player classes keeping track of players of the game.
        letterPoints: Counter class for storing the point awarded for each letter, without any modifiers.
    """
    def __init__(self):
        """Initializes Scrabbler class. Clears board, players, reloads dictionary and resets bag."""
        self.board = Board()
        self.bag = Bag()
        self.bag.loadLetterCounts('letter_counts_HUN.txt')
        self.players = []
        self.loadLetterPoints("letter_points_HUN.txt")
    
    def addPlayer(self, player):
        """Adds a new player to the game.
        
        Attributes:
            player: Player class to be appended to list of players.
        """
        self.players.append(player)
    
    def loadLetterPoints(self, filename):
        """Loads a text file which containts every valid letter and its score.

        Attributes:
            filename: String of the filename. File is assumed to be in the same directory as this .py runnable.
        """
        self.letterPoints = Counter()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, filename), mode='r', encoding="utf-8") as file:
            for line in file:
                (letter, point) = line.split()
                self.letterPoints[letter] = int(point)
    
    def wordProbability(self, word):
        """Checks the probability of drawing letters for a certain word from the current bag. Also considers different spellings, if the word can be created in multiple ways from the valid letter set.

        Attributes:
            word: String of the word to be checked.
        """
        probability = 0
        if len(word)>0:
            for spelling in self.spellings(word):
                if not self.bag.areLettersIn(spelling):
                    next
                letters = Counter(spelling)
                probability += math.prod([math.comb(self.bag.letters[letter],count) for letter, count in letters.items()]) / math.comb(self.bag.letters.total(), letters.total())
        return probability
    
    def lettersProbability(self, letters, draws=6):
        """Checks the probability of drawing a certain set of letters from the current bag. Also considers different spellings, if the word can be created in multiple ways from the valid letter set.

        Attributes:
            letters: String of the word to be checked.
            draws: Defaults to 6.
        """
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

    def findValidWordsRegex(self, letterset, n=10):
        letters = Counter(letterset)
        uniqueValidCharacters = ''.join(set(''.join(letters.keys())))
        expression = '^'
        for letter in letters:
            expression += '(?!(.* '+letter+' .*){'+str(letters[letter]+1)+'})'
            for character in letter:
                if character not in letters.keys():
                    expression += '(?!.* '+character+' .*)'
            if len(letter)>1:
                if letter[::-1] not in letters.keys():
                    expression += '(?!.* '+letter[::-1]+' .*)'
        expression += '[ '+uniqueValidCharacters+']*$'
        print(expression)

        reg = re.compile('{}'.format(expression))
        return sorted([word.split() for word in filter(reg.search, s.regexDictionary)], key=self.wordPoints, reverse=True)
    
    def findValidWords(self, letterset):
        return sorted([word for word in self.spellingDictionary if Counter(word)<=letterset], key=self.wordPoints, reverse=True)

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
    #player.hand=Counter("s zs sz e e d z é".split())
    #for letter in player.hand:
    #    for i in range(player.hand[letter]):
    #        s.bag.remove(letter)

    player.hand += s.bag.draw(7)

player = random.choice(s.players)
if player.isBot:
    print("Starting hand:")
    print(player.hand)
    print("Highest scoring valid words:")
    start = time.time()
    for word in s.findValidWords(player.hand)[:10]:
        print(s.wordPoints(word),' - ',word)
    end = time.time()
    print('Elapsed time: '+str(end - start))
    print("Same but with regex:")
    start = time.time()
    for word in s.findValidWordsRegex(player.hand)[:10]:
        print(s.wordPoints(word),' - ',word)
    end = time.time()
    print('Elapsed time: '+str(end - start))
    print("Highest chance to ace with following words (max 2 difference):")   
    for word in s.findPossibleWords(player.hand, 7, 2)[:10]:
        print(s.wordPoints(word),' - ',word,' - ',s.missingLetters(player.hand, word),' - ',s.lettersProbability(s.missingLetters(player.hand, word)))
    print("Chance to play specific word with specific spelling (k e ny e r e s):")
    word = "k e ny e r e s".split()
    print(s.wordPoints(word),' - ',word,' - ',s.missingLetters(player.hand, word),' - ',s.lettersProbability(s.missingLetters(player.hand, word)))


    s.playWord(player, player.startingMove())
print("Board after starting move:")
#s.board.draw()
print("New hand:")
print(player.hand)

#print("Top 10 most probable words for each length")
#for length in range(2,10):
#    print(s.top(length))