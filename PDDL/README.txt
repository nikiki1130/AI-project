# README.md

## Introduction
These PDDL files is utilized to generate plans suitable to be used for Game Pacman. It contains two domain files that represent the point of view of Pacman and the point of view of Ghost respectively. The Pacman domain models four main behavior for Pacman, avoiding meeting static ghosts, eating foods, coming back to home area, and eating ghosts when they are powered. Additionally, the Ghost domain models two key actions, eating static pacmans, avoiding meeting pacmans when they are scared and 

## Pacman Domain

### Predicates:

This domain firstly defines some predicates for all of pacman’s behaviour.
```
(:predicates (At ?p - posi)
                 (CapsulesAt ?p - posi)
                 (FoodAt ?p - posi)
                 (GhostAt ?p - posi)
                 (Connected ?pos1 ?pos2 - posi)
                 (Powered)
)
```

### Actions:

```
(:action move
                :parameters (?PosCurrent ?PosNext - posi)
                :precondition (and (At ?PosCurrent)
                                   (Connected ?PosCurrent ?PosNext)
                                   (not (GhostAt ?PosNext))
                                   (not (CapsulesAt ?PosNext)))
                :effect (and (At ?PosNext) 
                             (not (At ?PosCurrent))
                             (not (FoodAt ?PosNext))   
                        )
)
```
* **move:** Move and eat food if there is. This action is a combination of “just move” and “move and eat food”. That means when the next position of this pacman is not a Ghost or a Capsule, the pacman will move and eat the food on next step if there is. 

```
(:action eatCap
                :parameters(?PosCurrent ?PosCap - posi)
                :precondition(and (At ?PosCurrent)
                                  (CapsulesAt ?PosCap)
                                  (Connected ?PosCurrent ?PosCap))
                :effect (and (At ?PosCap)
                             (not (At ?PosCurrent))
                             (not (CapsulesAt ?PosCap))
                             (Powered)
                        )
)
```
* **eatCap:** Eat Capsule and be Powered. This action is utilized to eat capsule and become powered when its next step will meet a Capsule.

```
(:action eatGhost
                :parameters(?PosCurrent ?PosGhost - posi)
                :precondition(and (At ?PosCurrent)
                                  (GhostAt ?PosGhost)
                                  (Connected ?PosCurrent ?PosGhost)
                                  (Powered))
                :effect (and (At ?PosGhost)
                             (not (At ?PosCurrent))
                             (not (GhostAt ?PosGhost)))
)
```
* **eatGhost:** Eat Ghost. According to game specification, Pacman will become powered and Ghost will be Scared when the Pacman ate a Capsule. Therefore, the Pacman will act the eatGhost when its precondition is powered and there is a Ghost in its next step. 

## Pacman Problems

### Goals:

```
(:goal
        (and 
            (not (FoodAt p_0_0))
            (not (FoodAt p_1_0))
            (not (FoodAt p_0_2))
            (not (FoodAt p_0_4))
            (not (FoodAt p_2_3))
            (or 
                (At p_2_1)
                (At p_2_2)
                (At p_3_1)
                (At p_3_2)
            )
        )
)
```
The goal of this problems is to eat all Food and come back home area. 

### Problems: 

* **problem_pacman:** This problem is a 5*5 grid which contains five Food, two Ghost as well as one Capsule. This design is for checking Pacman is able to eat Food correctly and also can eat Ghost after eating a Capsule. In this problem, the initial position for Pacman is (2, 1) and after three steps, there is a Food at (0, 0). To choose the best path, this Pacman should firstly eat the Food (0, 0). However, there is a Ghost at (0, 1). Therefore, the Pacman goes to eat other Foods instead of eating Food (0, 0). Similarly, the only path to Food (2, 3) is held up by Ghost (1, 3). Therefore, the Pacman firstly eats the Capsule (0, 3) and becomes Powered. And then it goes to eat Ghost (1,3) and eat the Food (2, 3).

## Ghost Domain

### Predicates:

This domain defines some predicates for all of Ghost’s behaviour.
```
(:predicates (At ?p - posi)
                 (PacmanAt ?p - posi)
                 (Connected ?pos1 ?pos2 - posi)
                 (Scared)
                 (isStart ?p - posi)
)
```
* **Scared && isStart:** The initial status of Ghost is Scared. In this situation, the Ghost avoids meeting Pacman and it will return isStart position when it is ate by Pacman. 

### Actions:
```
(:action move
                :parameters (?PosCurrent ?PosNext - posi)
                :precondition (and (At ?PosCurrent)
                                   (Connected ?PosCurrent ?PosNext)
                                   (not (PacmanAt ?PosNext)))
                :effect (and (At ?PosNext) 
                             (not (At ?PosCurrent))
                        )
)
```
* **move:** This is the basic move action which just do move to next position when there is no Pacman. Since, in the corresponding Ghost Problem, Ghost is Scared in ':init'. 

```
(:action eatScared
                :parameters(?PosCurrent ?PosNext ?Start - posi)
                :precondition(and (At ?PosCurrent)
                                  (Scared)
                                  (PacmanAt ?PosNext)
                                  (isStart ?Start)
                                  (Connected ?PosCurrent ?PosNext))
                :effect (and (At ?Start)
                             (not (At ?PosCurrent))
                             (not (Scared))
                        )
)
```
* **eatScared:** Scared Ghost is ate by Pacman and returns to isStart position. According to our assumption, Ghost is Scared In initial situation. When its next position is Pacman, it is ate by Pacman and returns to the isStart position to start again with nonScared.

```
(:action eatNonScared
                :parameters(?PosCurrent ?PosNext - posi)
                :precondition(and (At ?PosCurrent)
                                  (PacmanAt ?PosNext)
                                  (Connected ?PosCurrent ?PosNext)
                                  (not (Scared)))
                :effect(and (At ?PosNext)
                             (not (At ?PosCurrent))
                             (not (PacmanAt ?PosNext))
                        )
)
```
* **eatNonScared:** According to our assumption, Ghost will be not Scared after eating the first Pacman. Then it will eat Pacman when there is in its next position. 

## Problem Ghost

### Goals:
```
(:goal
        (and 
            (not (PacmanAt p_0_4))
            (not (PacmanAt p_2_3))
            (not (PacmanAt p_4_4))
        )
)
```
The goal of the Ghost problem is to eat all Pacmans.

### Problems:

* **problem_ghost:**  This problem is a 5*5 grid which contains one Ghost as well as three Pacmans. The desgin is for checking if the Ghost which is scared can be ate by Pacman and the Ghost that is not Scared can eat Pacman. In thie problem, the Ghost is at initial position (1, 1) and it will go (0, 4) to eat the first Pacman and come back to isStart position. Then it becomes nonScared and continues to eat the rest Pacmans. 
