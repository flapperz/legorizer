import numpy as np
from copy import deepcopy
from _brick import *

import timeit
from random import random


def CheckBrickTouch(brick1, x1, y1, brick2, x2, y2):
    beginx1, endx1, beginy1, endy1 = brick1.GetBoundary(x1, y1)
    beginx2, endx2, beginy2, endy2 = brick2.GetBoundary(x2, y2)

    hTouch = (beginx1 == endx2) or (beginx2 == endx1)
    vTouch = (beginy1 == endy2) or (beginy2 == endy1)
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
    dict {
        (coord) : [ (lower coord1), (lower coord2), ... ]
    }

Blue Edges
----------

    dict of list of tuple 
    idx - z
    {
    idx:0 -> [((2,3),(3,4)), ((1,1),(2,3))]
    idx:1 -> [((1,1),(1,3)), ((x1,y1),(x2,y2))]  
        .
        .
    }

Uncovered Blue Edges
--------------------
    {
        <index in blue edges list> : redEdgeDist
                    .
                    .
                    .
    }

'''




class State():

    def __init__(self, sil, brickList, isCopy=False):
        # global reference
        self.sil = sil
        self.brickList = brickList
        if not isCopy:
            areaList = [b.area for b in brickList]
            self.maxBrick = max(areaList)
            self.minBrick = min(areaList)
            self.slotno = np.sum(self.sil)
        
        # field
        self.nodes = dict()
        self.brickNumber = 0

        self.blueEdges = { 0: [] }
        self.uncoveredBlueEdges = dict()

        self.redEdges = dict()

        self.dimZ = sil.shape[0]

        self.currentZ = 0
        self.currentLayerSil = np.zeros(sil[0].shape, dtype=bool)

        # Heuristic
        self.GS = 0
        self.gsEachBlueEdges = dict() #idx-gs
        self.currentLayerGH = 0
        self.GH = 0
        self.GA = 0

        self.MoveNextAvailLayer()

    def copy(self):
        s = State(self.sil, self.brickList, isCopy=True)

        s.maxBrick = self.maxBrick
        s.minBrick = self.minBrick

        s.brickNumber = self.brickNumber

        s.nodes = deepcopy(self.nodes)
        s.blueEdges = deepcopy(self.blueEdges)
        s.uncoveredBlueEdges = deepcopy(self.uncoveredBlueEdges)
        
        s.redEdges = deepcopy(self.redEdges)

        s.currentZ = self.currentZ
        s.currentLayerSil = np.array(self.currentLayerSil)

        s.slotno = self.slotno

        s.GS = self.GS
        s.gsEachBlueEdges = deepcopy(self.gsEachBlueEdges)
        s.GH = self.GH
        s.GA = self.GA
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
    
    def __ge__(self, other):
        return self.currentZ < other.currentZ
    
    def CountBrick(self):
        res = 0
        for k in self.nodes:
            for j in self.nodes[k]:
                res += len(self.nodes[k][j])
        return res

    def __lt__(self, other):
        return self.CountBrick() > other.CountBrick()

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

        res = 'current layer: {} brick number: {}\n'.format(self.currentZ, self.brickNumber)

        # if z == self.dimZ:
        #     z -= 1

        # if z not in self.nodes:
        #     res += 'empty'
        #     return res

        # for j in self.nodes[z]:
        #     for i in self.nodes[z][j]:
        #         brick = nodes[z][j][i]
        #         beginx, endx, beginy, endy = brick.GetBoundary(i,j)
        #         printTable[beginy][beginx]  = '#'
        #         printTable[endy-1][beginx]  = '#'
        #         printTable[beginy][endx-1]  = '#'
        #         printTable[endy-1][endx-1]  = '#'
                
        #         if brick.w == 1:
        #             printTable[beginy][beginx] = 'u'
        #             printTable[endy-1][beginx] = 'n'
        #         if brick.h == 1:
        #             printTable[beginy][beginx] = '('
        #             printTable[beginy][endx-1] = ')'
        #         if brick.h == 1 and brick.w == 1:
        #             printTable[beginy][beginx] = '#'

        #         for ix in range(beginx+1, endx-1):
        #             printTable[beginy][ix] = HORPIPE
        #             printTable[endy-1][ix] = HORPIPE
        #         for jx in range(beginy+1, endy-1):
        #             printTable[jx][beginx] = VERPIPE
        #             printTable[jx][endx-1] = VERPIPE

        
        # res += '-'*2*dimx + '\n'
        # for j in range(len(printTable)-1,-1,-1):
        #     res += '|'
        #     for e in printTable[j]:
        #         res += e + '|'
        #     res += '\n' + '-'*2*dimx + '\n'

        return res

    def PrintSchematic(self):
        maxz = self.currentZ
        nodes = self.nodes

        dimy, dimx = self.currentLayerSil.shape
        VERPIPE = u'\u2551'
        HORPIPE = u'\u2550'
        print("schematic till present")
        
        for z in range(maxz+1):
            
            printTable = [[" " for i in range(dimx)] for j in range(dimy)]
            res = 'layer: {}\n'.format(z)

            if z == self.dimZ:
                continue

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
            print(res)
        print("#####################")

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
                        # update blue edges
                        newState.blueEdges[z] += checkBlueEdges

                        # update red edges
                        topVert = (px,py,z)
                        newState.redEdges[topVert] = []
                        if checkRedEdges:
                            newState.redEdges[topVert] = [pair[1] for pair in checkRedEdges]

                        # update GS
                        
                        if z-1 in self.blueEdges:
                            covereds = [pair[1] for pair in checkRedEdges]
                            for idx, edges in enumerate(self.blueEdges[z-1]):
                                if edges[0] in covereds and edges[1] in covereds:
                                    # print("idx = {}, gsEach = {}".format(idx, self.gsEachBlueEdges))
                                    gsi = self.gsEachBlueEdges.pop(idx,0)
                                    self.GS -= gsi

                        newState.AddBrickNoCheck(px,py,brick) # may move next state here

                        nextStates.append(newState)
                        break

        return nextStates

    ### EDGE

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
        self.brickNumber += 1
        self._SetNode(x,y,z, brick)
        # self.currentLayerGH = self.CalNewBrickGH()
        # self.GA += brick.area/self.slotno

        self.MoveNextAvailLayer()

        return True

    ### BLUE EDGE
    def AssignPrevLayerUncoveredBlueEdges(self, prevLayerBlueEdges, z):
        '''
        calCache
        --------

            {
                coord : {
                    z1 : set {<child coord1>, <child coord2>, ...}
                    .
                    .
                }
            }
        '''
        calCache = dict()
        
        
    
        for idx in range(len(prevLayerBlueEdges)):
            coord1, coord2 = prevLayerBlueEdges[idx]

            # pre register
            if coord1 not in calCache:
                calCache[coord1] = {
                    z-1: set(self.redEdges[ coord1 ])
                }
            if coord2 not in calCache:
                calCache[coord2] = {
                    z-1: set(self.redEdges[ coord2 ])
                }

            considerZ = z-1
            # first set to infinity
            self.uncoveredBlueEdges[idx] = np.Inf
            # consider each layer
            while considerZ >= 0:

                if considerZ not in calCache[coord1]:
                    calCache[coord1][considerZ] = set()
                    for upperChild in calCache[coord1][considerZ+1]:
                        calCache[coord1][considerZ].update( set( self.redEdges[upperChild] ) )
                thisLayerChild1 = calCache[coord1][considerZ]

                if considerZ not in calCache[coord2]:
                    calCache[coord2][considerZ] = set()
                    for upperChild in calCache[coord2][considerZ+1]:
                        calCache[coord2][considerZ].update( set( self.redEdges[upperChild] ) )
                thisLayerChild2 = calCache[coord2][considerZ]

                # if (considerZ == 3):
                #     print( "cal cache", calCache )
                # if len(thisLayerChild1.intersection(thisLayerChild2)):
                if thisLayerChild1.intersection(thisLayerChild2):
                    self.uncoveredBlueEdges[idx] = z-considerZ
                    break

                considerZ -= 1
                      
    ### HEURISTIC
    def CalNewLayerGS(self):
        self.gsEachBlueEdges = dict()
        # GS T
        T = 2
        P1 = 0.1
        P2 = 0.5
        P3 = 1.0

        prevZ = self.currentZ - 1
        
        m = len(self.uncoveredBlueEdges)
        res = 0
        for idx in range(m):
            y = self.uncoveredBlueEdges[idx]
            gsi = 0
            if y <= T:
                gsi = P1/m
            elif y == np.Inf:
                gsi = P3/m
            elif (y > T):
                gsi = P2/m
            self.gsEachBlueEdges[idx] = gsi
            res += gsi
        
        return res

    def CalHeuristic(self):
        

        return self.GS - self.currentZ
        # return self.GS + self.GH + self.currentLayerGH
        return self.GS + self.GH + self.currentLayerGH - self.GA
        # return self.GS + self.currentLayerGH

    def CalNewBrickGH(self):
        z = self.currentZ
        slotno = np.sum(self.sil[z])
        assignno = 0
        brickCount = 0
        nodes = self.nodes
        if z in nodes:
            for j in nodes[z]:
                for i in nodes[z][j]:
                    assignno += nodes[z][j][i].area
                    brickCount += 1

        notassignslot = slotno - assignno

        n = notassignslot + brickCount
        return (n*self.maxBrick - slotno)/(n* (self.maxBrick-self.minBrick) )
        
        
        # return (brickCount*self.maxBrick - assignno) / (brickCount *(self.maxBrick-self.minBrick) )

        

    ### LAYER

    def IsLayerFull(self):
        return np.sum( np.bitwise_xor(self.currentLayerSil, self.sil[self.currentZ] ) ) == 0

    def _MoveNextLayer(self):

        self.currentLayerSil = np.zeros(self.sil[0].shape, dtype=bool)
        self.currentZ += 1

        # LOG
        # print('blue edges: ', self.blueEdges)
        # print('uncovered under layer {}'.format(self.currentZ), self.uncoveredBlueEdges)

        # new blueEdge
        self.blueEdges[self.currentZ] = []

        prevLayer = self.currentZ - 1
        prevLayerBlueEdges = []
        if prevLayer in self.blueEdges:
            prevLayerBlueEdges = self.blueEdges[prevLayer] # pass previous layer to uncovered calculation
        
        delLayer = self.currentZ - 2
        if delLayer in self.blueEdges:
            del self.blueEdges[delLayer]
        
        # print( "z = {}".format(self.currentZ))
        # print( self.blueEdges)

        # self.uncoveredBlueEdges = dict()
        self.AssignPrevLayerUncoveredBlueEdges(prevLayerBlueEdges, prevLayer)
        self.GS += self.CalNewLayerGS()
        # self.GH += self.currentLayerGH
        self.currentLayerGH = 0

    def MoveNextAvailLayer(self):

        if (self.currentZ >= self.dimZ):
            return

        while self.IsLayerFull():
            self._MoveNextLayer()
            if (self.currentZ == self.dimZ):
                break