# Course             : COMP90054
# File               : qlearning.py
# GroupName          : Alive
# Author(LogID)      : Fei TENG(fteng1), Zhe TANG(ztang2), Haoran SUN(haorans)

class QlearningAgent(CaptureAgent):


  def __init__(self,index, timeForComputing = .1, alpha=0.95, epsilon=0.05, gamma=0.8, numTraining=10,):
    """
    Sets options, which can be passed in via the Pacman command line using -a alpha=0.5,...
    alpha    - learning rate
    epsilon  - exploration rate
    gamma    - discount factor
    numTraining - number of training episodes, i.e. no learning after these many episodes
    """
    self.alpha = float(alpha)
    self.epsilon = float(epsilon)
    self.discount = float(gamma)
    self.numTraining = int(numTraining)
    self.index = index
    self.q_values = util.Counter()
    self.weights = util.Counter()
    self.episodesSoFar = 0


    self.red = None

    self.agentsOnTeam = None


    self.distancer = None


    self.observationHistory = []


    self.timeForComputing = timeForComputing


    self.display = None

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


  def computeAction(self,state):
    max_action = None
    max_q_val = 0
    for action in state.getLegalActions(self.index):
      q_val = self.getQValue(state,action)
      if q_val > max_q_val or max_action is None:
        max_q_val = q_val
        max_action = action
    return max_action


  def computeValue(self,state):
    q_vals = []
    actions = state.getLegalActions(self.index)
    for action in actions:
      q_vals.append(self.getQValue(state,action))
    if len(actions) == 0:
      return 0.0
    else:
      return max(q_vals)


  def chooseAction(self, state):
    self.lastState = state



    # Pick Action
    actions = state.getLegalActions(self.index)
    if util.flipCoin(self.epsilon):
      self.lastAction = random.choice(actions)
      return random.choice(actions)
    else:
      self.lastAction = self.computeAction(state)
      return self.computeAction(state)


  def update(self, state, action, nextState, reward):
    features = self.getFeatures(state,action)
    nextactions = nextState.getLegalActions(self.index)

    counter = 0
    for feature in features:
      difference = 0
      if len(nextactions) == 0:
        difference = reward - self.getQValue(state, action)
      else:
        difference = (reward + self.discount * max([self.getQValue(nextState, nextAction) for nextAction in nextactions])) - self.getQValue(state, action)

      self.weights[feature] = self.weights[feature] + self.alpha * difference * features[feature]
      counter += 1

  def getpolicy(self,state):
    return self.computeAction(state)

  def getvalue(self,state):
    return self.computeValue(state)

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    # Compute score from successor state
    features['successorScore'] = self.getScore(successor)+1

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0:
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Compute distance to closest ghost
    myPos = successor.getAgentState(self.index).getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
    if len(inRange) > 0:
      positions = [agent.getPosition() for agent in inRange]
      closest = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
      closestDist = self.getMazeDistance(myPos, closest)
      if closestDist <= 5:
        features['distanceToGhost'] = closestDist

    # Compute if is pacman
    features['isPacman'] = 1 if successor.getAgentState(self.index).isPacman else 0

    return features

  def getQValue(self, state, action):
    qvalue = 0
    features = self.getFeatures(state,action)
    weights = self.getWeights(state,action)

    for feature in features:
      qvalue += features[feature] * weights[feature]
    return qvalue

  def getWeights(self,gameState,action):
    # If opponent is scared, the agent should not care about distanceToGhost
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    inRange = filter(lambda x: not x.isPacman and x.getPosition() != None, enemies)
    if len(inRange) > 0:
      positions = [agent.getPosition() for agent in inRange]
      closestPos = min(positions, key=lambda x: self.getMazeDistance(myPos, x))
      closestDist = self.getMazeDistance(myPos, closestPos)
      closest_enemies = filter(lambda x: x[0] == closestPos, zip(positions, inRange))
      for agent in closest_enemies:
        if agent[1].scaredTimer > 0:
          return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 0, 'isPacman': 0}

    # Weights normally used
    return {'successorScore': 200, 'distanceToFood': -5, 'distanceToGhost': 2, 'isPacman': 0}

  def observeTransition(self, state,action,nextState,deltaReward):
    self.episodeRewards += deltaReward
    self.update(state,action,nextState,deltaReward)


  def observationFunction(self, state):
    if not self.lastState is None:
      reward = self.money(state) - self.money(self.lastState)

      self.observeTransition(self.lastState, self.lastAction, state, reward)
    return state

  def registerInitialState(self, state):
    self.start = state.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, state)
    self.startEpisode()


  def startEpisode(self):
    self.lastState = None
    self.lastAction = None
    self.episodeRewards = 0.0

  def stopEpisode(self):

    if self.episodesSoFar < self.numTraining:
      self.accumTrainRewards += self.episodeRewards
    else:
      self.accumTestRewards += self.episodeRewards
    self.episodesSoFar += 1
    if self.episodesSoFar >= self.numTraining:
      self.epsilon = 0.0  # no exploration
      self.alpha = 0.0  # no learning

  def money(self,state):
    foods = self.getFood(state).asList()
    pos = state.getAgentPosition(self.index)

    minDistance = min([self.getMazeDistance(pos, food) for food in foods])
    money = -minDistance - 10 * len(foods)

    return money