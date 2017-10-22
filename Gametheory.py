# Course             : COMP90054
# File               : Gametheory.py
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
    def __init__(self, index, epsilon=0, timeForComputing=.1, depth=4, times=20, alpha=0.9):
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



        # define global variables which represent two ghosts position
        enemy_1 = gameState.getAgentState(self.getOpponents(gameState)[0])
        enemy_2 = gameState.getAgentState(self.getOpponents(gameState)[1])

        # initialize the variables which is the predict location of two ghosts
        pos_1 = enemy_1.getPosition()
        pos_2 = enemy_2.getPosition()

        goodation = self.computeAction(gameState,pos_1,pos_2)
        if self.index == 2:
            print "this is Number "+ str(self.index)+' choose action ' + goodation




        actions = gameState.getLegalActions(self.index)
        actions.remove('Stop')






        if util.flipCoin(self.epilon):

            return random.choice(actions)
        else:
            return goodation

    def computeAction(self, state,pos_1,pos_2):
        actions = state.getLegalActions(self.index)
        actions.remove('Stop')
        values = [self.mainevaluate(state, a,pos_1,pos_2) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        if self.index == 2:
          print bestActions
          print maxValue

        return random.choice(bestActions)

    def mainevaluate(self, state, action,pos_1,pos_2):
        nextStateValue = self.getbasicValue(state, action)

        lefttimes = self.times
        while (lefttimes > 0):
            nextStateValue += self.deepsearch(state, self.depth,pos_1,pos_2)
            lefttimes = lefttimes - 1
        return nextStateValue

    def deepsearch(self, state, depth,pos_1,pos_2):
        onetimevalue = 0
        newstate = state
        while (depth > 0):
            fakeactions = newstate.getLegalActions(self.index)
            fakeactions.remove('Stop')
            fakeaction = random.choice(fakeactions)
            pos_1, pos_2 = self.newPosition(newstate, fakeaction, pos_1, pos_2)
            onetimevalue += self.getdeepValue(newstate, fakeaction,pos_1,pos_2) * self.alpha
            newstate = newstate.generateSuccessor(self.index, fakeaction)
            depth = depth - 1
        return onetimevalue

    def getbasicValue(self, state, action):
        features = self.getfeatures(state, action)
        weights = self.getweights(state, action)
        value = 0




        for feature in features:

            value += features[feature] * weights[feature]
        if self.index == 2:
            print action
            print features,value

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

                if enemy.isPacman:
                    if Mydis < Matedis:
                        features['eatPacman'] = self.getMazeDistance(myPos, enemy.getPosition())
                elif ((myPos in enemyPosiblePos)or myPos==self.start):

                    minDistance = min([self.getMazeDistance(myPos, ourfood) for ourfood in ourfoods])
                    features['runback'] = minDistance
                    features['distanceToFood'] = 0
                    features['gost-one-step'] = -100


        if len(foods) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foods])
            features['distanceToFood'] = minDistance



        if ((nextState.getAgentState(self.index).numCarrying > 0 and self.runbackCheck(nextState)) or nextState.getAgentState(self.index).numCarrying > 2):

          features['distanceToFood']=0
          features['eatfood'] = 0
          if len(Capsules) > 0 and self.runbackCheck(nextState):
            backdistance = min([self.getMazeDistance(myPos, Capsule) for Capsule in Capsules])
            features['runback'] = backdistance
          else:
            backdistance = min([self.getMazeDistance(myPos, self.start)])
            features['runback'] = backdistance


        features['notdeadend'] = 0
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
            if 2*Sharon > self.powerTimer:
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0

        else:
            features['isPowered'] = 0.0


        return features

    def getweights(self, state, action):
        return {'successorScore': 2000, 'eatPacman': -2, 'gost-one-step': 5, 'distanceToFood': -1, 'eatfood': -10,
                'runback': -0.05, 'notdeadend': 0, 'isPowered':50000,'eatCapsule':-100}


    def getdeepValue(self,newstate,fakeaction,pos_1,pos_2):

        features = self.getdeepfeatures(newstate, fakeaction,pos_1,pos_2)
        weights = self.getdeepweights(newstate, fakeaction)
        value = 0

        for feature in features:
            value += features[feature] * weights[feature]

        if self.index == 2:
          print fakeaction
          print features, value

        return value

    def getdeepfeatures(self, newstate, fakeaction, pos_1, pos_2):
      features = util.Counter()

      nextState = newstate.generateSuccessor(self.index, fakeaction)
      myState = nextState.getAgentState(self.index)
      myPos = myState.getPosition()

      enemy_1 = newstate.getAgentState(self.getOpponents(newstate)[0])
      enemy_2 = newstate.getAgentState(self.getOpponents(newstate)[1])

      features['dis_enemy'] = 0

      if ((pos_1 != None or pos_2 != None) and myState.isPacman == True and not self.isPowered()):
        if pos_1 != None and enemy_1.isPacman == False:
          distance1 = self.getMazeDistance(myPos, pos_1)
          if distance1 == 0:
            features['dis_enemy'] = -1
        if pos_2 != None and enemy_2.isPacman == False:
          distance2 = self.getMazeDistance(myPos, pos_2)
          if distance2 == 0:
            features['dis_enemy'] = -1

      return features

    def getdeepweights(self, newstate, fakeaction):
      return {'successorScore': 0, 'dis_enemy': 120}

    def newPos(self, state, pos, direction):

      # like getsuccessor(self, state, action)
      newpos = pos
      if pos != None:
        if direction == 'north':
          newpos = (pos[0], pos[1] + 1)
        elif direction == 'south':
          newpos = (pos[0], pos[1] - 1)
        elif direction == 'west':
          newpos = (pos[0] - 1, pos[1])
        elif direction == 'east':
          newpos = (pos[0] + 1, pos[1])
        else:
          newpos = pos

        if not state.hasWall(int(newpos[0]), int(newpos[1])):
          return newpos
        else:
          return pos

      else:
        return pos

    def newPosition(self, state, action, pos_1, pos_2):

      # get pacman location
      myState = state.getAgentState(self.index)
      myPos = myState.getPosition()

      enemy_1 = state.getAgentState(self.getOpponents(state)[0])
      enemy_2 = state.getAgentState(self.getOpponents(state)[1])

      pos_1 = pos_1
      pos_2 = pos_2

      newpos = []
      value_enemy1 = []
      value_enemy2 = []

      newpos[:] = []
      value_enemy1[:] = []
      value_enemy2[:] = []

      action = ['north', 'south', 'west', 'east']

      if pos_1 != None and not enemy_1.isPacman:
        for i in range(0, 4):
          new = self.newPos(state, pos_1, action[i])
          newpos.append(new)
          value_enemy1.append(self.getMazeDistance(myPos, new))
        feature_value1 = min(value_enemy1)
        pos_1 = newpos[value_enemy1.index(feature_value1)]

      newpos[:] = []

      if pos_2 != None and not enemy_2.isPacman:
        for i in range(0, 4):
          new = self.newPos(state, pos_2, action[i])
          newpos.append(new)
          value_enemy2.append(self.getMazeDistance(myPos, new))
        feature_value2 = min(value_enemy2)
        pos_2 = newpos[value_enemy2.index(feature_value2)]

      return pos_1, pos_2



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



                if enemy.isPacman:
                    if Mydis < Matedis:
                        features['eatPacman'] = self.getMazeDistance(myPos, enemy.getPosition())

                elif (myPos in enemyPosiblePos) or myPos == self.start:
                    minDistance = min([self.getMazeDistance(myPos, ourfood) for ourfood in ourfoods])
                    features['runback'] = minDistance
                    features['distanceToFood'] = 0
                    features['gost-one-step'] = -100

        if len(foods) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in bottomfoods])
            features['distanceToFood'] = minDistance


        if ((nextState.getAgentState(self.index).numCarrying > 0 and self.runbackCheck(nextState)) or nextState.getAgentState(self.index).numCarrying > 2):
          features['eatfood'] = 0
          features['distanceToFood']=0

          if len(Capsules) > 0 and self.runbackCheck(nextState):
            backdistance = min([self.getMazeDistance(myPos, Capsule) for Capsule in Capsules])
            features['runback'] = backdistance
          else:
            backdistance = min([self.getMazeDistance(myPos, self.start)])
            features['runback'] = backdistance


        features['notdeadend'] = 0
        if (self.runbackCheck(nextState) and len(actions) == 1):
            features['notdeadend'] = 1

        if (self.isPowered()):


            features['isPowered'] = float(self.powerTimer) / float(POWERCAPSULETIME)
            features['eatfood'] = 10 * len(foods)
            features['distanceToFood'] = 2* Sharon
            features['gost-one-step'] = 0
            if 2*Sharon > self.powerTimer or nextState.getAgentState(self.index).numCarrying >6 :
                backdistance = min([self.getMazeDistance(myPos, self.start)])
                features['runback'] = backdistance
                features['distanceToFood'] = 0

        else:
            features['isPowered'] = 0.0

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
