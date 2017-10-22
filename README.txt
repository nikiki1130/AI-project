# README

## Group Members

If you have any problems running this code, please contact us :)

* Fei Teng
fteng1@student.unimelb.edu.au

* Haoran Sun
haorans@student.unimelb.edu.au

* ZHE TANG
ztang2@student.unimelb.edu.au

## Approach

We implement several versions. And change the structures while we implement those algorithms. The whole structure is like this:
The Pacman will detect all its next state. And from all its next state, it will go X depth randomly. And do that Y times. Each next state an average value. The action it takes based one those values. Based on that, this pacman could choose a better way to go.

About the game theory, we will have a fake ghost decision. When we see it, we will Hypothesis that it will run to us. And iteration it in our depth search.
