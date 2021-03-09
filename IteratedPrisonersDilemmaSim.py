"""
IteratedPrisonersDilemmaSim

Simulates iterated prisoners dilemma either among chosen strategies or against the user.

Cooperating = not telling on the other person, represented as True in this program
Ratting out/defecting = telling on the other person, represented as False in this program

@author: Kiera Gross
kiera.gross@stonybrook.edu
"""

from enum import Enum
import random
import math

# these are the payoffs for each of the options
both_rat = 0  # both players tell on each other
neither_rat = 5  # both players do not tell on each other
ratter = 3  # the player that told on the other (who didn't tell)
rattee = -1  # the player who was told on (but didn't tell themselves)


# these are the different strategies implemented in this program
class Strategy(Enum):
    # nice - always cooperates
    NICE = 1
    # greedy - always rats
    GREEDY = 2
    # tit for tat - cooperates at first, then does whatever the opponent did the previous round
    TITFORTAT = 3
    # nice until not - cooperates until the opponent rats, then rats until the opponent cooperates twice
    NICEUNTIL = 4
    # average strategy - starts with cooperating then does whatever the opponent has done the most of in previous turns
    AVESTRAT = 5
    # random strategy - starts with cooperating, then picks a random move from the set of the opponent's previous turns
    RANSTRAT = 6
    # random - randomly selects cooperating or ratting
    RANDOM = 7
    # user - placeholder strategy for a user
    USER = 8

"""
prisoner class - contains all the information on a prisoner for one simulation of iterated prisoner's dilemma vs 
another prisoner. Also contains the strategy it follows.
"""
class Prisoner:
    def __init__(self, strat):
        self.strategy = strat
        self.turns = []
        self.elim_round = 0
        self.final_score = 0
        self.elim = False

    def add_turns(self, move):
        self.turns.append(move)

    def reset_turns(self):
        self.turns = []

    def add_to_score(self, num):
        self.final_score = self.final_score + num

    def reset_score(self):
        self.final_score = 0

    def set_elim_round(self, num):
        self.elim_round = num
        self.elim = True

    def eliminated(self):
        self.elim = True


""""
implements the strategy of "nice until not" or NICEUNTIL

:param last move: the last move that was played by NICEUNTIL, turns: the other player's turns so far
:returns the play (True for cooperative, False for defecting)
"""
def nice_until_not(last_move, turns):
    if len(turns) == 0:
        return True
    if last_move:
        if turns[-1]:
            return True
        else:
            return False
    elif len(turns) == 1:
        return False
    else:
        if turns[-1] and turns[-2]:
            return True
        else:
            return False


""""
implements the strategy of "average strategy" or AVESTRAT

:param turns: the other player's turns so far
:returns the play (True for cooperative, False for defecting)
"""
def average_strategy(turns):
    if len(turns) == 0:
        return True
    ave = 0
    for i in range(len(turns)):
        if turns[i]:
            ave = ave + 1
        else:
            ave = ave - 1
    if ave >= 0:
        return True
    else:
        return False


"""
uses the strategy's name to determine the correct logic to use & finds if they would cooperate or defer that turn
:param strat: the strategy, turns: the opponent's turns so far, our_turns: the turns we've played so far
:return True for cooperate, false for defer
"""
def strategy_to_payoff(strat, turns, our_turns):
    # some strategies rely on the last move the person took rather than the opponent
    # if there was no previous turns, we just set this value to None
    if len(our_turns) == 0:
        last_move = None
    else:
        last_move = our_turns[-1]

    # this would be a switch statement, but python doesn't do that... enjoy a bunch of ifs!
    if strat.value == 4:
        return nice_until_not(last_move, turns)
    elif strat.value == 5:
        return average_strategy(turns)
    elif strat.value == 6:
        if len(turns) == 0:
            return True
        else:
            return turns[random.randint(0, len(turns)-1)]
    elif strat.value == 7:
        return bool(random.getrandbits(1))
    elif strat.value == 3:
        if len(turns) == 0:
            return True
        else:
            return turns[-1]
    elif strat.value == 1:
        return True
    else:           # if it's not any of the others, it's GREEDY
        return False


"""
uses the choice determined by strategy_to_payoff to calculate what the payoffs are for each player
:param prisoner1: player one (a prisoner), prisoner2: player two (a prisoner), isuser: true if prisoner2 is a user, 
userchoice: the decision (cooperate or defer) of the user
:return prisoner1, prisoner2
"""
def dilemma(prisoner1, prisoner2, isuser, userchoice):
    # we use True to be cooperate (don't rat out) and false to be accuse (do rat out)
    prisoner1_choice = strategy_to_payoff(prisoner1.strategy, prisoner2.turns, prisoner1.turns)
    prisoner2_choice = userchoice
    if not isuser:
        prisoner2_choice = strategy_to_payoff(prisoner2.strategy, prisoner1.turns, prisoner2.turns)

    # keep track of what their choice was
    prisoner1.add_turns(prisoner1_choice)
    prisoner2.add_turns(prisoner2_choice)

    # if they both cooperated, they both get the best score
    if prisoner1_choice and prisoner2_choice:
        prisoner1.add_to_score(neither_rat)
        prisoner2.add_to_score(neither_rat)
    else:
        if prisoner1_choice:  # if prisoner1 cooperated, but not both
            prisoner1.add_to_score(rattee)
            prisoner2.add_to_score(ratter)
        elif prisoner2_choice:  # if prisoner2 cooperated, but not both
            prisoner1.add_to_score(ratter)
            prisoner2.add_to_score(rattee)
        else:  # if neither cooperated
            prisoner1.add_to_score(both_rat)
            prisoner2.add_to_score(both_rat)

    return prisoner1, prisoner2


"""
pits two prisoners against each other for the specified number of rounds or until one is eliminated. In a tie, one is 
eliminated "at random" (since the order they are put in is random)
:param prisoner1: player one (a prisoner), prisoner2: player two (a prisoner), elim_num: the lowest value a prisoner 
can hit, round_max: the maximum number of rounds to play
:return prisoner1 & prisoner2, winner first
"""
def match(prisoner1, prisoner2, elim_num, round_max):
    # reset the prisoners, set the round number
    prisoner1.reset_score()
    prisoner1.reset_turns()
    prisoner2.reset_score()
    prisoner2.reset_turns()
    round_num = 1

    # face off until one is eliminated or until the number of rounds is reached
    while round_num <= round_max and prisoner1.final_score > elim_num and prisoner2.final_score > elim_num:
        prisoner1, prisoner2 = dilemma(prisoner1, prisoner2, False, None)
        round_num = round_num + 1

    # no matter what, the one with the lower score is eliminated, if there's a tie, one is eliminated anyway
    if prisoner1.final_score <= prisoner2.final_score:
        prisoner1.eliminated()
        return prisoner2, prisoner1
    else:
        prisoner2.eliminated()
        return prisoner1, prisoner2


"""
sets up pairwise matches among a group of prisoners, keeping the final match data for each
:param prisoners: a list of prisoners, elim_num: the lowest value a prisoner can hit, round_max: the maximum number of 
rounds to play
:return a list of all the prisoners, with the winner in the last spot
"""
def set_up_matches(prisoners, elim_num, round_max):
    final_prisoners = []
    current_winners = []
    current_winners.extend(prisoners)

    while len(current_winners) > 1:
        # clear out the winners list to add the new winners only
        current_winners.clear()
        # shuffle the prisoners to make it fair
        random.shuffle(prisoners)

        # if there's an odd number of prisoners, just add the middle one to the winner's list
        if len(prisoners) % 2 == 1:
            extra = prisoners[len(prisoners)//2]
            current_winners.append(extra)

        # set the prisoners at opposite ends of the list against each other, working towards the middle of the list
        for i in range(0, math.floor(len(prisoners)/2)):
            winner, loser = match(prisoners[i], prisoners[len(prisoners)-i-1], elim_num, round_max)
            current_winners.append(winner)
            final_prisoners.append(loser)  # this is to keep track of the final values of prisoners

        # the new set of prisoners to work with is the ones that won
        prisoners.clear()
        prisoners.extend(current_winners)

    # makes the last prisoner in the list the overall winner
    final_prisoners.append(current_winners[0])

    # return the final state of all prisoners
    return final_prisoners


"""
gives a random prisoner from the strategies defined
:return a random prisoner
"""
def random_prisoner():
    types = [Strategy.NICE, Strategy.GREEDY, Strategy.RANDOM, Strategy.TITFORTAT, Strategy.RANSTRAT,
             Strategy.AVESTRAT, Strategy.NICEUNTIL]
    prisoner = Prisoner(types[random.randint(0, 6)])
    return prisoner


"""
adds a number of prisoners with a specific strategy to a given list
:param strat: the strategy, number: the number of prisoners to add, prisoners: the list to add to
:return prisoners, the list with the things in it
"""
def add_prisoner(strat, number, prisoners):
    while number > 0:
        number = number - 1
        prisoners.append(Prisoner(strat))
    return prisoners


"""
battles a randomly selected strategy against the user for as long as they want.
"""
def versus_user():
    print("Setting up your match...")
    prisoner = random_prisoner()
    user = Prisoner(Strategy.USER)
    keep_playing = True
    user_choice = None
    while keep_playing:
        selected = False
        while not selected:
            choice = input("Type 'c' for cooperate, or 'd' for defect: ")
            if choice == 'c' or choice == 'C':
                user_choice = True
                selected = True
            elif choice == 'd' or choice == 'D':
                user_choice = False
                selected = True
            else:
                print("Not a valid input." + "\n")
        prisoner, user = dilemma(prisoner, user, True, user_choice)
        if user_choice:
            print("You chose to cooperate.")
        else:
            print("You chose to defect.")
        if prisoner.turns[-1]:
            print("The other prisoner chose to keep quiet." + "\n")
        else:
            print("The other prisoner chose to rat you out!" + "\n")
        print("Opponent Score: " + str(prisoner.final_score) + "\n")
        print("Your Score: " + str(user.final_score) + "\n")
        keep_playing_string = input("Do you want to keep playing? Hit 'y' for yes, 'n' for no: ")
        if keep_playing_string is not 'y' and keep_playing is not 'Y':
            keep_playing = False
            print("Thanks for playing!")
        else:
            print("Let's continue!")


"""
the main function - finds out whether the user wants to pit prisoners against each other or play against a random 
prisoner themself. handles a bunch of user input and interactions.
"""
def main():
    vs_or_sim = input("Would you like to put strategies against each other? Hit 'y' for yes, 'n' for no: ")
    if vs_or_sim is not 'y' and vs_or_sim is not 'Y':
        vs_or_sim = input("Would you like to play against a randomly selected strategy? Hit 'y' for yes, 'n' for no: ")
        if vs_or_sim is not 'y' and vs_or_sim is not 'Y':
            print("That's all this program can do. Have a nice day!")
            exit(0)
        else:
            versus_user()
            print("Have a nice day!")
            exit(0)
    else:
        prisoners = []
        print("There are 7 different strategies to select from. Each strategy will appear with a definition. "
              "Type in the number of that strategy you would like to be included in this simulation." + "\n")
        print("The NICE strategy only cooperates." + "\n")
        num_nice = input("please input the number of NICE you would like: ")
        if int(num_nice) > 0:
            prisoners = add_prisoner(Strategy.NICE, int(num_nice), prisoners)
        print("The GREEDY strategy only defects." + "\n")
        num_greed = input("please input the number of GREEDY you would like: ")
        if int(num_greed) > 0:
            prisoners = add_prisoner(Strategy.GREEDY, int(num_greed), prisoners)
        print("The RANDOM strategy selects a play at random." + "\n")
        num_rand = input("please input the number of RANDOM you would like: ")
        if int(num_rand) > 0:
            prisoners = add_prisoner(Strategy.RANDOM, int(num_rand), prisoners)
        print("The TITFORTAT strategy cooperates, then does whatever the other prisoner did last turn." + "\n")
        num_titfortat = input("please input the number of TITFORTAT you would like: ")
        if int(num_titfortat) > 0:
            prisoners = add_prisoner(Strategy.TITFORTAT, int(num_titfortat), prisoners)
        print("The NICEUNTIL strategy cooperates until the other prisoner defects. "
              "Then it defects until the other prisoner cooperates twice in a row." + "\n")
        num_niceuntil = input("please input the number of NICEUNTIL you would like: ")
        if int(num_niceuntil) > 0:
            prisoners = add_prisoner(Strategy.NICEUNTIL, int(num_niceuntil), prisoners)
        print("The RANSTRAT strategy cooperates, then randomly selects a move from the other prisoner's past moves."
              + "\n")
        num_ranstrat = input("please input the number of RANSTRAT you would like: ")
        if int(num_ranstrat) > 0:
            prisoners = add_prisoner(Strategy.RANSTRAT, int(num_ranstrat), prisoners)
        print("The AVESTRAT strategy cooperates, then plays whatever move the other prisoner has played most so far."
              + "\n")
        num_avestrat = input("please input the number of AVESTRAT you would like: ")
        if int(num_avestrat) > 0:
            prisoners = add_prisoner(Strategy.AVESTRAT, int(num_avestrat), prisoners)
        num_rounds = input("How many rounds do you want the maximum to be?: ")
        elim_num = input("Under what value do you think a player should be eliminated?: ")
        print("Preparing to run simulation..." + "\n")
        finished_prisoners = set_up_matches(prisoners, int(elim_num), int(num_rounds))
        print("Simulation complete. Here are the results: " + "\n" +
              "Note: If the round number is zero, they were not eliminated by a certain round via the elimination value"
              + "\n")
        for i in range(len(finished_prisoners)):
            if i == len(finished_prisoners) - 1:
                print("The overall winner was: ")
            print("final score in last match: " + str(finished_prisoners[i].final_score) + " ... round elminated: " + str(finished_prisoners[i].elim_round) +
                  " ... strategy: " + finished_prisoners[i].strategy.name + "\n")
        print("I hope you enjoyed! :)")


if __name__ == '__main__':
    main()
