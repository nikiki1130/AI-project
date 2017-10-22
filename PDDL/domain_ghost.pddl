﻿(define (domain ghost)
    (:requirements :typing :conditional-effects)
    (:types posi)
    (:predicates (At ?p - posi)
                 (PacmanAt ?p - posi)
                 (Connected ?pos1 ?pos2 - posi)
                 (Scared)
                 (isStart ?p - posi)
    )

    (:action move
                :parameters (?PosCurrent ?PosNext - posi)
                :precondition (and (At ?PosCurrent)
                                   (Connected ?PosCurrent ?PosNext)
                                   (not (PacmanAt ?PosNext)))
                :effect (and (At ?PosNext) 
                             (not (At ?PosCurrent))
                        )
    )
    
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
)