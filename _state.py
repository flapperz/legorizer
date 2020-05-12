import numpy as np
from copy import deepcopy
from _brick import *

from random import random

class State():

    def __init__(self, sil, brickList, isCopy=False):
        # global reference
        self.sil = sil
        self.brickList = brickList
        
        # field
        self.nodes = dict()
        self.redEdges = dict()
        self.blueEdges = dict()
        self.dimZ = sil.shape[0]

        self.currentZ = 0
        self.currentLayerSil = np.zeros(sil[0].shape, dtype=bool)

        self.MoveNextAvailLayer()

    def copy(self):
        s = State(self.sil, self.brickList, isCopy=True)
        s.nodes = deepcopy(self.nodes)
        s.redEdge = deepcopy(self.redEdges)
        s.blueEdges = deepcopy(self.blueEdges)

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

                    if self.IsNewBrickValid(px,py,brick):
                        newState = self.copy()
                        newState.AddBrick(px,py, brick)

                        nextStates.append(newState)
                        break

        return nextStates

    def CalHeuristic(self):
        return 1/(self.currentZ * 400 + np.sum(self.currentLayerSil) +random() ) #TODO

    
    ### NODE

    def _SetNode(self, x, y, z, brick):

        if z not in self.nodes:
            self.nodes[z] = dict()

        if y not in self.nodes[z]:
            self.nodes[z][y] = dict()

        self.nodes[z][y][x] = brick
        beginx, endx, beginy, endy = brick.GetBoundary(x,y)
        self.currentLayerSil[beginy:endy,beginx:endx] = True

    def IsNewBrickValid(self, x, y, newbrick):

        z = self.currentZ
        dimy,dimx = self.currentLayerSil.shape

        beginx, endx, beginy, endy = newbrick.GetBoundary(x,y)

        if beginx < 0 or endx > dimx:
            return False
        if beginy < 0 or endy > dimy:
            return False

        for i in range(beginx, endx):
            for j in range(beginy, endy):
                if not self.sil[z][j][i]:
                    return False
                if self.currentLayerSil[j][i]:
                    return False
        return True

    def AddBrick(self, x, y, brick):
        ''' O( IsNewBrickValid) '''
        z = self.currentZ
        # if not self.IsNewBrickValid(x,y, brick):
        #     return False
        # TODO set red, blue edges
        self._SetNode(x,y,z, brick)

        self.MoveNextAvailLayer()

        return True

    ### BLUE EDGE
    def AddBlueEdgesForNodes(self, nodecoord):
        nx, ny, nz = nodecoord
        brick = self.nodes[nz][ny][nx]
        
        for j in self.nodes[nz]:
            for i in self.nodes[nz][j]:
                # if IsBrickAdjacent
                pass

        # self._AddOneDirEdge()
        # self._AddOneDirEdge

    def _AddOneDirEdge(self, coord1, coord2 ):

        x, y, z = coord1
        if z not in self.blueEdges:
            self.blueEdges[z] = dict()
        if y not in self.nodes[z]:
            self.blueEdges[z][y] = dict()

        self.blueEdges[z][y][x] = coord2 


    ### LAYER

    def IsLayerFull(self):
        return np.sum( np.bitwise_xor(self.currentLayerSil, self.sil[self.currentZ] ) ) == 0

    def _MoveNextLayer(self):
        self.currentLayerSil = np.zeros(self.sil[0].shape, dtype=bool)
        self.currentZ += 1

    def MoveNextAvailLayer(self):

        if (self.currentZ >= self.dimZ):
            return

        while self.IsLayerFull():
            self._MoveNextLayer()
            if (self.currentZ == self.dimZ):
                break