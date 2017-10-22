# Course             : COMP90054
# File               : myTeam.py
# GroupName          : Alive
# Author(LogID)      : Fei TENG(fteng1), Zhe TANG(ztang2), Haoran SUN(haorans)

# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent, AgentFactory
import random, time, util
from game import Directions, Agent
import game
from util import nearestPoint


POWERCAPSULETIME=40

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='MCTSAgent', second='BottomAgent', numTraining=0):
    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class MCTSAgent(CaptureAgent):


    def __init__(self, index, epsilon=0, timeForComputing=.1, depth=2, times=20, alpha=0.9):
        self.depth = depth
        self.times = times
        self.alpha = float(alpha)
        self.powerTimer = 0

        self.epilon = float(epsilon)
        CaptureAgent.__init__(self, index, timeForComputing=.1)

    def runbackCheck(self, state):
        myState = state.getAgentState(self.index)
        myPos = myState.getPosition()
        enemy_1 = state.getAgentState(self.getOpponents(state)[0])
        enemy_2 = state.getAgentState(self.getOpponents(state)[1])
        dis = 1000
        if enemy_1.getPosition() != None:
            dis = self.getMazeDistance(myPos, enemy_1.getPosition())
        if enemy_2.getPosition() != None:
            dis = min(dis, self.getMazeDistance(myPos, enemy_2.getPosition()))

        if (dis < 3 and state.getAgentState(self.index).isPacman):
            return True
        else:
            return False

    def registerInitialState(self, gameState):

        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)


    def isPowered(self):
        return self.powerTimer > 0



    def getSuccessor(self, gameState, action):
        """
    Finds the next successor which is a grid position (location tuple).
    """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        if self.powerTimer > 0:
            self.powerTimer -= 1

        enemyIndexList = self.getOpponents(gameState)
        # for enemyIndex in enemyIndexList:
        #     enemy = gameState.getAgentState(enemyIndex)
        #     print enemy

        goodation = self.computeAction(gameState)
        # if self.index == 2:
        #     print "this is Number "+ str(self.index)+' choose action ' + goodation




        actions = gameState.getLegalActions(self.index)
        actions.remove('Stop')






        if util.flipCoin(self.epilon):

            return random.choice(actions)
        else:
            return goodation

    def computeAction(self, state):
        actions = state.getLegalActions(self.index)
        actions.remove('Stop')
        values = [self.mainevaluate(state, a) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def mainevaluate(self, state, action):
        nextStateValue = self.getbasicValue(state, action)

        lefttimes = self.times
        while (lefttimes > 0):
            nextStateValue += self.deepsearch(state, self.depth)
            lefttimes = lefttimes - 1
        return nextStateValue

    def deepsearch(self, state, depth):
        onetimevalue = 0
        newstate = state
        while (depth > 0):
            fakeactions = newstate.getLegalActions(self.index)
            fakeactions.remove('Stop')
            fakeaction = random.choice(fakeactions)
            onetimevalue += self.getdeepValue(newstate, fakeaction) * self.alpha
            newstate = newstate.generateSuccessor(self.index, fakeaction)
            depth = depth - 1
        return onetimevalue

    def getbasicValue(self, state, action):



        successor = self.getSuccessor(state, action)

        # Get own position
        myState = successor.getAgentState(self.index)

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]


        if self.getScore(state)>3 and len(invaders)>0 :
            features = self.getDefencefaeture(state,action)
            weights = self.getDefenceweight(state,action)
        else :
            features = self.getfeatures(state, action)
            weights = self.getweights(state, action)
        value = 0




        for feature in features:

            value += features[feature] * weights[feature]
        # if self.index == 2:
        #     print action
        #     print features,value

        return value



    def getfeatures(self, state, action):
        features = util.Counter()
        nextState = state.generateSuccessor(self.index, action)
        actions = nextState.getLegalActions(self.index)

        myState = nextState.getAgentState(self.index)
        myPos = myState.getPosition()

        myteam = self.getTeam(state)
        myteam.remove(self.index)
        teammate_index = myteam[0]


        matePos = state.getAgentState(teammate_index).getPosition()


        mateActions = state.getLegalActions(teammate_index)
        matePosiblePos = []
        for mateAction in mateActions:
            mateNextState = state.generateSuccessor(teammate_index, mateAction)
            pos = mateNextState.getAgentState(teammate_index).getPosition()
            matePosiblePos.append(pos)

        foods = self.getFood(nextState).asList()
        ourfoods = self.getFoodYouAreDefending(nextState).asList()

        if foods!=[]:
            Sharon = min([self.getMazeDistance(myPos, food) for food in foods])
        else:
            Sharon = 0



        features['runback'] = 0
        if foods != []:
            features['eatfood'] = len(foods)
        else:
            features['eatfood'] = 0


        Capsules = self.getCapsules(state)

        if Capsules != 0:
            features['eatCapsule'] = len(Capsules)
        if myPos in Capsules:
            features['eatCapsule'] = 0




        enemyIndexList = self.getOpponents(state)

        for enemyIndex in enemyIndexList:
            enemy = state.getAgentState(enemyIndex)
            if enemy.getPosition() != None:
                enemyActions = state.getLegalActions(enemyIndex)
                enemyPosiblePos = []
                for enemyAction in enemyActions:
                    enemyNextState = state.generateSuccessor(enemyIndex, enemyAction)
                    pos = enemyNextState.getAgentState(enemyIndex).getPosition()
                    enemyPosiblePos.append(pos)
                Mydis = self.getMazeDistance(myPos, enemy.getPosition())
                Matedis = self.getMazeDistance(matePos, enemy.getPosition())

                if enemy.isPacman and not nextState.getAgentState(self.index).isPacman:
                    if Mydis < Matedis:
                        features['eatPacman'] = self.getMazeDistance(myPos, enemy.getPosition())
                elif ((myPos in enemyPosiblePos)or myPos==self.start):

                    if ourfoods != []:
                        minDistance = min([self.getMazeDistance(myPos, ourfood) for ourfood in ourfoods])
                        features['runback'] = minDistance
                    features['distanceToFood'] = 0
                    features['gost-one-step'] = -100


        if len(foods) > 0 and foods != []:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foods])
            features['distanceToFood'] = minDistance



        if ((nextState.getAgentState(self.index).numCarrying > -1 and self.runbackCheck(state)) or nextState.getAgentState(self.index).numCarrying > 2):

          features['distanceToFood']=0
          features['eatfood'] = 0
          if len(Capsules) > 0 and self.runbackCheck(state):
            backdistance = min([self.getMazeDistance(myPos, Capsule) for Capsule in Capsules])
            features['runback'] = backdistance
          else:
            backdistance = min([self.getMazeDistance(myPos, self.start)])
            features['runback'] = backdistance


        features['notdeadend'] = 0
        actions.remove('Stop')
        if (self.runbackCheck(nextState) and len(actions) == 1):
            features['notdeadend'] = 1

        # Compute score from successor state
        features['successorScore'] = self.getScore(nextState)



        for Capsule in self.getCapsules(state):
            if myPos == Capsule or Capsule in matePosiblePos:
                self.powerTimer = POWERCAPSULETIME









        if (self.isPowered()):

            features['isPowered'] = float(self.powerTimer) / float(POWERCAPSULETIME)
            features['eatfood'] = 10 * len(foods)
            features['gost-one-step'] = 0
            if 2*Sharon > self.powerTimer and nextState.getAgentState(self.index).numCarrying > 0:
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0

        else:
            features['isPowered'] = 0.0

        if state.getAgentState(self.index).isPacman and not self.isPowered():
            if self.runbackCheck(state) and len(Capsules)==0:
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0
                features['eatfood'] =0
        return features

    def getweights(self, state, action):
        return {'successorScore': 2000, 'eatPacman': -2, 'gost-one-step': 5, 'distanceToFood': -1, 'eatfood': -50,
                'runback': -0.05, 'notdeadend': 0, 'isPowered':50000,'eatCapsule':-100}


    def getdeepValue(self,newstate,fakeaction):

        features = self.getdeepfeatures(newstate, fakeaction)
        weights = self.getdeepweights(newstate, fakeaction)
        value = 0

        for feature in features:
            value += features[feature] * weights[feature]

        return value


    def getdeepfeatures(self,newstate, fakeaction):
        features = util.Counter()
        nextState = newstate.generateSuccessor(self.index, fakeaction)
        features['successorScore'] = self.getScore(nextState)
        return features


    def getdeepweights(self,newstate, fakeaction):
        return {'successorScore': 0.0001}

    def getDefencefaeture(self,state,action):
        features = util.Counter()
        successor = self.getSuccessor(state, action)

        # Get own position
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # List invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() != None]

        enemyIndexList = self.getOpponents(state)
        Target_Index = -1
        TargetDistance = 10000
        for enemyIndex in enemyIndexList:
            enemy = state.getAgentState(enemyIndex)
            if enemy.getPosition() != None and enemy.isPacman:
                DistancetoOurbase = self.getMazeDistance(self.start, enemy.getPosition())
                if TargetDistance >DistancetoOurbase:
                    TargetDistance=DistancetoOurbase
                    Target_Index = enemyIndex





        for enemyIndex in enemyIndexList:
            enemy = state.getAgentState(enemyIndex)
            if enemy.getPosition() != None and not enemy.isPacman:
                enemyActions = state.getLegalActions(enemyIndex)
                enemyPosiblePos = []
                for enemyAction in enemyActions:
                    enemyNextState = state.generateSuccessor(enemyIndex, enemyAction)
                    pos = enemyNextState.getAgentState(enemyIndex).getPosition()
                    enemyPosiblePos.append(pos)
                if ((myPos in enemyPosiblePos)or myPos==self.start):
                    features['gost-one-step'] = -100
        # Get number of invaders
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
            enemyDist = self.getMazeDistance(myPos, state.getAgentState(Target_Index).getPosition())
            # Find closest invader
            features['invaderDistance'] = enemyDist



        return features

    def getDefenceweight(self,state,action):
        return {'gost-one-step': 5,'numInvaders':-2,'invaderDistance': -5}





class BottomAgent(MCTSAgent):


    def getfeatures(self, state, action):
        features = util.Counter()
        nextState = state.generateSuccessor(self.index, action)
        actions = nextState.getLegalActions(self.index)
        myPos = nextState.getAgentState(self.index).getPosition()




        foods = self.getFood(nextState).asList()
        ourfoods = self.getFoodYouAreDefending(nextState).asList()
        bottomfoods = self.leasty(foods)
        ourbottomfoods = self.leasty(ourfoods)
        if foods!=[]:
            Sharon = min([self.getMazeDistance(myPos, food) for food in foods])
        else:
            Sharon = 0

        myteam = self.getTeam(state)
        myteam.remove(self.index)
        teammate_index = myteam[0]

        matePos = state.getAgentState(teammate_index).getPosition()

        mateActions = state.getLegalActions(teammate_index)
        matePosiblePos = []
        for mateAction in mateActions:
            mateNextState = state.generateSuccessor(teammate_index, mateAction)
            pos = mateNextState.getAgentState(teammate_index).getPosition()
            matePosiblePos.append(pos)

        if foods !=[]:
            features['eatfood'] = len(foods)
        else:
            features['eatfood'] = 0

        features['runback'] = 0



        Capsules =      self.getCapsules(state)

        if Capsules != 0:
            features['eatCapsule'] = len(Capsules)
        if myPos in Capsules:
            features['eatCapsule'] = 0



        #set Capsules
        for Capsule in self.getCapsules(state):
            if myPos == Capsule or Capsule in matePosiblePos:
                self.powerTimer = POWERCAPSULETIME











        enemyIndexList = self.getOpponents(state)
        for enemyIndex in enemyIndexList:
            enemy = state.getAgentState(enemyIndex)
            if enemy.getPosition() != None:
                enemyActions = state.getLegalActions(enemyIndex)
                enemyPosiblePos = []
                for enemyAction in enemyActions:
                    enemyNextState = state.generateSuccessor(enemyIndex, enemyAction)
                    pos = enemyNextState.getAgentState(enemyIndex).getPosition()
                    enemyPosiblePos.append(pos)

                Mydis = self.getMazeDistance(myPos, enemy.getPosition())
                Matedis = self.getMazeDistance(matePos, enemy.getPosition())



                if enemy.isPacman and not nextState.getAgentState(self.index).isPacman:
                    if Mydis < Matedis:
                        features['eatPacman'] = self.getMazeDistance(myPos, enemy.getPosition())

                elif (myPos in enemyPosiblePos) or myPos == self.start:
                    if ourfoods != []:
                        minDistance = min([self.getMazeDistance(myPos, ourfood) for ourfood in ourfoods])
                        features['runback'] = minDistance
                    features['distanceToFood'] = 0
                    features['gost-one-step'] = -100

        if len(foods) > 0 and bottomfoods != []:
            minDistance = min([self.getMazeDistance(myPos, food) for food in bottomfoods])
            features['distanceToFood'] = minDistance


        if ((nextState.getAgentState(self.index).numCarrying > -1 and self.runbackCheck(state)) or nextState.getAgentState(self.index).numCarrying > 2):
          features['eatfood'] = 0
          features['distanceToFood']=0

          if len(Capsules) > 0 and self.runbackCheck(state):
            backdistance = min([self.getMazeDistance(myPos, Capsule) for Capsule in Capsules])
            features['runback'] = backdistance
          else:
            backdistance = min([self.getMazeDistance(myPos, self.start)])
            features['runback'] = backdistance
        actions.remove('Stop')

        features['notdeadend'] = 0
        if (self.runbackCheck(nextState) and len(actions) == 1):
            features['notdeadend'] = 1

        if (self.isPowered()):


            features['isPowered'] = float(self.powerTimer) / float(POWERCAPSULETIME)
            if foods != []:
                features['eatfood'] = 10 * len(foods)
            features['distanceToFood'] = 2* Sharon
            features['gost-one-step'] = 0
            if (2*Sharon > self.powerTimer and nextState.getAgentState(self.index).numCarrying > 0) or nextState.getAgentState(self.index).numCarrying >6 :
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0

        else:
            features['isPowered'] = 0.0

        if state.getAgentState(self.index).isPacman and not self.isPowered():
            if self.runbackCheck(state) and len(Capsules)==0:
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0
                features['eatfood'] = 0




        # Compute score from successor state
        features['successorScore'] = self.getScore(nextState)
        return features

    def getweights(self, state, action):

        Scores = self.getScore(state)
        if Scores < 0:
            return {'successorScore': 2000, 'eatPacman': -1, 'gost-one-step': 5, 'distanceToFood': -2,
                    'eatfood': -10,'runback': -0.1, 'notdeadend': 0, 'isPowered': 50000, 'eatCapsule': -100}
        else:
            return {'successorScore': 2000, 'eatPacman': -2, 'gost-one-step': 5, 'distanceToFood': -1, 'eatfood': -10,
                'runback': -0.1, 'notdeadend': 0,'isPowered':50000,'eatCapsule':-100}

    def leasty(self, foodlist):
        if foodlist!=[]:

            minimal = foodlist[0][1]
            lindex = []

            for i in range(len(foodlist)):
                if foodlist[i][1] < minimal:
                    minimal = foodlist[i][1]
                    lindex[:] = []
                    lindex.append(foodlist[i])
                elif foodlist[i][1] == minimal:
                    lindex.append(foodlist[i])
            return lindex