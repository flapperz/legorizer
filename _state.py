import numpy as np
from copy import deepcopy
from _brick import *

from random import random


def CheckBrickTouch(brick1, x1, y1, brick2, x2, y2):
    beginx1, endx1, beginy1, endy1 = brick1.GetBoundary(x1, y1)
    beginx2, endx2, beginy2, endy2 = brick2.GetBoundary(x2, y2)

    hTouch = (beginx1 == endx2) or (beginx2 == endx1)
    vTouch = (beginy1 == endy1) or (beginy2 == endy1)
    return (hTouch and not vTouch ) or (not hTouch and vTouch)



def CheckBrickConnect(bricku, xu, yu, brickd, xd, yd):
    beginxu, endxu, beginyu, endyu = bricku.GetBoundary(xu, yu)
    beginxd, endxd, beginyd, endyd = brickd.GetBoundary(xd, yd)
    
    if beginxu >= endxd or endxu-1 < beginxd:
        return False
    
    if beginyu >= endyd or endyu-1 < beginyd:
        return False

    return True

def Dist(coord1, coord2):
    dist = (coord1[0]-coord2[0], coord1[1]-coord2[1], coord1[2]-coord2[2])
    return (dist[0]**2 + dist[1]**2 + dist[2]**2)**0.5
    # return int(dist[0] + dist[1] + dist[2])


'''
brick coordinate

(-.5,-.5)---(0,-.5)---(.5,-.5)---(1,-.5)---(xxxxxx) . .
    |                    |                     |
    |                    |                     |
(-.5, 0  )---(0, 0)---(.5, 0)----(1, 0)----(xxxxxx) . .
    |                    |                     |
    .                    .                     .
    . . . .          . . . . .             . . . . . .
    .                    .                     .

    leftmost: -0.5 (impossible position)

    fraction .5 when length of brick is even -> [ O | O ]
                                              -.5  .5   1.5
                                                    ^

                                                [ O | O | O ]
                                                  0   1   2
                                                      ^

Red Edges
---------

    distance matrix
     + + +  (1,1,1) (1,2,2) (2,3,4) (x,y,z)
    (1,1,1)        |       |       |
    (1,2,2)        |       |       |
    (2,3,4)        |       |       |
    (x,y,z)        |       |       |

    RedEdgesLabel = [(1,1,1), (1,2,2), (2,3,4)]

    newRedEdges = dict {
        (coord1) : [(coord2, dist), ...]
            .
            .
            .
    }

Red Edges Redesign
------------------

Blue Edges
----------

    list of list of tuple 
    idx - z
    [
    idx:0 -> [((2,3),(3,4)), ((1,1),(2,3))]
    idx:1 -> [((1,1),(1,3)), ((x1,y1),(x2,y2))]  
        .
        .
    ]

'''




class State():

    def __init__(self, sil, brickList, isCopy=False):
        # global reference
        self.sil = sil
        self.brickList = brickList
        
        # field
        self.nodes = dict()
        self.redEdges = np.zeros((0,0), dtype=float)
        self.redEdgesLabel = []
        self.newRedEdges = dict()

        self.blueEdges = [[]]

        self.dimZ = sil.shape[0]

        self.currentZ = 0
        self.currentLayerSil = np.zeros(sil[0].shape, dtype=bool)

        self.MoveNextAvailLayer()

    def copy(self):
        s = State(self.sil, self.brickList, isCopy=True)
        s.nodes = deepcopy(self.nodes)
        s.blueEdges = deepcopy(self.blueEdges)
        s.redEdges = deepcopy(self.redEdges)
        s.redEdgesLabel = deepcopy(self.redEdgesLabel)
        s.newRedEdges = deepcopy(self.newRedEdges)

        s.currentZ = self.currentZ
        s.currentLayerSil = np.array(self.currentLayerSil)
        return s

    def __eq__(self, other):

        if type(self) != type(other):
            return False

        mynodes = self.nodes
        onodes = other.nodes

        if set(mynodes.keys()) != set(onodes.keys()):
            return False
            
        for k in mynodes:
            if set(mynodes[k].keys()) != set(onodes[k].keys()):
                return False
            
        for k in mynodes:
            for j in mynodes[k]:
                if set(mynodes[k][j].keys()) != set(onodes[k][j].keys()):
                    return False
        
        return True
        
    def __hash__(self):
        nodes = self.nodes
        hashval = 0
        for k in nodes:
            hashval += int(k)*311 % 8000051
            for j in nodes[k]:
                hashval = (hashval + int(j)*313) % 7500071 + 113
                for i in nodes[k][j]:
                    hashval += (int(i)*317  + nodes[k][j][i].w*557 + nodes[k][j][i].h*563)
        return hashval
    
    def __repr__(self):
        z = self.currentZ
        nodes = self.nodes

        dimy, dimx = self.currentLayerSil.shape
        VERPIPE = u'\u2551'
        HORPIPE = u'\u2550'
        printTable = [[" " for i in range(dimx)] for j in range(dimy)]

        res = 'current layer: {}\n'.format(self.currentZ)

        if z == self.dimZ:
            z -= 1

        if z not in self.nodes:
            res += 'empty'
            return res

        for j in self.nodes[z]:
            for i in self.nodes[z][j]:
                brick = nodes[z][j][i]
                beginx, endx, beginy, endy = brick.GetBoundary(i,j)
                printTable[beginy][beginx]  = '#'
                printTable[endy-1][beginx]  = '#'
                printTable[beginy][endx-1]  = '#'
                printTable[endy-1][endx-1]  = '#'
                
                if brick.w == 1:
                    printTable[beginy][beginx] = 'u'
                    printTable[endy-1][beginx] = 'n'
                if brick.h == 1:
                    printTable[beginy][beginx] = '('
                    printTable[beginy][endx-1] = ')'
                if brick.h == 1 and brick.w == 1:
                    printTable[beginy][beginx] = '#'

                for ix in range(beginx+1, endx-1):
                    printTable[beginy][ix] = HORPIPE
                    printTable[endy-1][ix] = HORPIPE
                for jx in range(beginy+1, endy-1):
                    printTable[jx][beginx] = VERPIPE
                    printTable[jx][endx-1] = VERPIPE

        
        res += '-'*2*dimx + '\n'
        for j in range(len(printTable)-1,-1,-1):
            res += '|'
            for e in printTable[j]:
                res += e + '|'
            res += '\n' + '-'*2*dimx + '\n'

        return res

    def IsFinish(self):
        return self.currentZ == self.dimZ

    def GetNextStates(self):
        '''O ( dimx * dimy * No brick * O( Add ) )'''
        z = self.currentZ
        dimy, dimx = self.currentLayerSil.shape
        nextStates = []

        for j in range(dimy):
            for i in range(dimx):

                if not self.sil[z][j][i]:
                    continue
                if self.currentLayerSil[j][i]:
                    continue

                for brick in self.brickList:
                    px = i
                    py = j
                    if brick.w % 2 == 0:
                        px += 0.5
                    if brick.h %2 == 0:
                        py += 0.5

                    isValid, checkBlueEdges, checkRedEdges = self.CheckNewBrick(px,py,brick)
                    if isValid:
                        newState = self.copy()
                        newState.AddBrickNoCheck(px,py,brick)
                        
                        # update blue and red edges
                        newState.blueEdges += checkBlueEdges
                        newState.newRedEdges[(px,py,z)] = []
                        newState.AddNewRedEdges(checkRedEdges)

                        nextStates.append(newState)
                        break

        return nextStates

    def CalHeuristic(self):
        return 1/(self.currentZ * 400 + np.sum(self.currentLayerSil) + random() ) #TODO

    ### EDGE
    def calNewShortestPath(self):
        # floyd warshall
        V, _ = self.redEdges.shape
        for k in range(V):
            for i in range(V):
                for j in range(V): 
                    self.redEdges[i][j] = min(self.redEdges[i][j],
                                            self.redEdges[i][k], self.redEdges[k][j])
        print(self.redEdges) #TODO delete
        print(self.redEdgesLabel)

    def AddNewRedEdges(self, checkRedEdges):
        ''' add checkRedEdges from checkNewBrick '''
        for (coord1, coord2) in checkRedEdges:
            if coord1 not in self.newRedEdges:
                self.newRedEdges[coord1] = []
            self.newRedEdges[coord1].append((coord2, Dist(coord1, coord2)))

    ### NODE

    def _SetNode(self, x, y, z, brick):

        if z not in self.nodes:
            self.nodes[z] = dict()

        if y not in self.nodes[z]:
            self.nodes[z][y] = dict()

        self.nodes[z][y][x] = brick
        beginx, endx, beginy, endy = brick.GetBoundary(x,y)
        self.currentLayerSil[beginy:endy,beginx:endx] = True

    def CheckNewBrick(self, x, y, newbrick):
        ''' return isValid, blueEdges, redEdges '''
        z = self.currentZ
        dimy,dimx = self.currentLayerSil.shape
        beginx, endx, beginy, endy = newbrick.GetBoundary(x,y)

        if beginx < 0 or endx > dimx:
            return False, [], []
        if beginy < 0 or endy > dimy:
            return False, [], [] 

        curZ = self.currentZ

        blueEdges = []
        redEdges = []

        # Check in silhoullet and not overlap
        for i in range(beginx, endx):
            for j in range(beginy, endy):
                if not self.sil[z][j][i]:
                    return False, [], []
                if self.currentLayerSil[j][i]:
                    return False, [], []


        # blueEdges
        if curZ in self.nodes:
            for j in self.nodes[curZ]:
                for i in self.nodes[curZ][j]:
                    otherBrick = self.nodes[curZ][j][i]
                    isTouch = CheckBrickTouch(newbrick, x, y, otherBrick, i, j)
                    if isTouch:
                        blueEdges.append( ((x,y,curZ), (i,j,curZ)) )

        # redEdges
        prevZ = curZ - 1
        if prevZ in self.nodes:
            for j in self.nodes[prevZ]:
                for i in self.nodes[prevZ][j]:
                    otherBrick = self.nodes[prevZ][j][i]
                    isConnect = CheckBrickConnect(newbrick, x, y, otherBrick, i, j)
                    if isConnect:
                        redEdges.append( ((x,y,curZ), (i,j,prevZ)) )


        return True, blueEdges, redEdges 

    def AddBrickNoCheck(self, x, y, brick):
        ''' O( IsNewBrickValid) '''
        z = self.currentZ
        self._SetNode(x,y,z, brick)

        self.MoveNextAvailLayer()

        return True

    ### BLUE EDGE


    ### LAYER

    def IsLayerFull(self):
        return np.sum( np.bitwise_xor(self.currentLayerSil, self.sil[self.currentZ] ) ) == 0

    def _MoveNextLayer(self):
        self.currentLayerSil = np.zeros(self.sil[0].shape, dtype=bool)
        self.currentZ += 1

        self.blueEdges.append([])

        # update red edge
        nOld, _ = self.redEdges.shape
        nNew = len(self.newRedEdges)
        oldRedEdges = self.redEdges

        # recalculate red edge
        self.redEdges = np.full((nOld+nNew, nOld+nNew), 9999, dtype=float)
        self.redEdges[0:nOld, 0:nOld] = oldRedEdges
        self.redEdgesLabel += self.newRedEdges.keys()
        for coord, vList in self.newRedEdges.items():
            for v in vList:
                coord2 = v[0]
                dist = v[1]
                
                idx = self.redEdgesLabel.index(coord)
                idx2 = self.redEdgesLabel.index(coord2)

                self.redEdges[idx, idx2] = dist
                self.redEdges[idx2, idx] = dist

        self.newRedEdges = dict()

        self.calNewShortestPath()

    def MoveNextAvailLayer(self):

        if (self.currentZ >= self.dimZ):
            return

        while self.IsLayerFull():
            self._MoveNextLayer()
            if (self.currentZ == self.dimZ):
                break