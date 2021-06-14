import sys
from pprint import pprint
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QPushButton
from PyQt5.QtGui import QIcon
import pickle
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QPlainTextEdit
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
import sys, random
import pickle
import random
import numpy as np
import scipy.spatial
from PyQt5.QtCore import QPoint
import collections
import math
import time
import heapq
import tkinter as tk
import random

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
points = []
edge_list = []
number_level_nodes = []
levels = 0
node_colour = []
result_path = []
paths = dict()
visited_set = dict()
counter = 0
iteration = 0


#My code
infinity=10000000
alpha=-infinity
beta=infinity
alpha1=-infinity
beta1=infinity
first_childs=[]
result=""
visited_nodes=[]
result_nodes=[]

#This function randomly generate leaf node values for the game
def generate_values(count):
    global points
    for i in range(count):
        integer = random.randint(10,100)
        points[i].value = integer

#This function generate the coordinates of points of trees for visualisation purposes
def generate_points():
    global points
    global levels
    global number_level_nodes
    global node_colour

    levels = 4

    count = 0
    level = 4
    for i in range(0, 1320, 20):
        count += 1
        node = Node(True, -1, 100+i, 750, level)
        points.append(node)

    number_level_nodes.append(count)
    count = 0

    generate_values(len(points))

    level = 3
    for i in range(100, 1200, 35):
        count += 1
        node = Node(False, -1, 100+i, 600, level)
        points.append(node)

    number_level_nodes.append(count)
    count = 0

    # generate_values(len(points))


    level = 2
    for i in range(250, 1050, 85):
        count += 1
        node = Node(True, -1, 100+i, 450, level)
        points.append(node)

    number_level_nodes.append(count)
    count = 0

    level = 1
    for i in range(375, 950, 105):
        count += 1
        node = Node(False, -1, 100 + i, 300, level)
        points.append(node)

    number_level_nodes.append(count)
    count = 0

    level = 0
    node = Node(True, -1, 728, 150, level)
    points.append(node)
    node_colour = [0 for p in points]
    number_level_nodes.append(1)

#This function generates the edges of the tree
def generate_edges():
    global edge_list
    global number_level_nodes
    global points
    root = points[-1]

    for i in range(-7, -1, 1):
        edge = [(root.x_coord, root.y_coord),(points[i].x_coord, points[i].y_coord)]
        edge_list.append(edge)

    mapping_array = [2 for p in range(6)]
    indexes = random.sample(range(6), 2)
    mapping_array[indexes[0]] = 1
    mapping_array[indexes[1]] = 1

    j_low = 98
    for i in range(108, 114, 1):
        count = 0
        for j in range(mapping_array[i-108]):
            edge = [(points[i].x_coord, points[i].y_coord), (points[j_low + j].x_coord, points[j_low + j].y_coord)]
            edge_list.append(edge)
            count += 1
        j_low += count

    mapping_array = [3 for p in range(10)]
    indexes = random.sample(range(10), 2)
    mapping_array[indexes[0]] = 4
    mapping_array[indexes[1]] = 4

    j_low = 66
    for i in range(98, 108, 1):
        count = 0
        for j in range(mapping_array[i - 98]):
            edge = [(points[i].x_coord, points[i].y_coord), (points[j_low + j].x_coord, points[j_low + j].y_coord)]
            edge_list.append(edge)
            count += 1
        j_low += count

    mapping_array = [2 for p in range(32)]
    indexes = random.sample(range(32), 2)
    mapping_array[indexes[0]] = 3
    mapping_array[indexes[1]] = 3

    j_low = 0
    for i in range(66, 98, 1):
        count = 0
        for j in range(mapping_array[i - 66]):
            edge = [(points[i].x_coord, points[i].y_coord), (points[j_low + j].x_coord, points[j_low + j].y_coord)]
            edge_list.append(edge)
            count += 1
        j_low += count

# Sets the first child index for each internal node in the tree in list first_childs
def setFirstChildIndexes(self,edge_list) :

    #first_childs.append(((e[0][0],e[0][1]),0))
    count=0
    for i in range(len(edge_list)) :

        
        if i == 0 :
            curr_edge=edge_list[i]
           # print("Adding ",curr_edge[0][0],curr_edge[0][1],":", 0);
            first_childs.append(((curr_edge[0][0],curr_edge[0][1]),0))
            continue
        else :
            prev_edge=edge_list[i-1]
            curr_edge=edge_list[i]

            if prev_edge[0][0]== curr_edge[0][0] and prev_edge[0][1]==curr_edge[0][1] :
                count=count+1
            elif ( prev_edge[0][0] == curr_edge[0][0] and prev_edge[0][1] != curr_edge[0][1]) or ( prev_edge[0][0] != curr_edge[0][0] and prev_edge[0][1] == curr_edge[0][1]) or ( prev_edge[0][0] != curr_edge[0][0] and prev_edge[0][1] != curr_edge[0][1]) :
                count=count+1
               # print("Adding ",curr_edge[0][0],curr_edge[0][1],":", count);
                first_childs.append(((curr_edge[0][0],curr_edge[0][1]),count))


class Node:
    def __init__(self, isMax, value, x_coord, y_coord, level):
        self.isMax = isMax
        self.value = value
        self.level = level
        self.x_coord = x_coord
        self.y_coord = y_coord

class Tree(QMainWindow):

#This is where you have to write you solution, according to the assignment whihc was given to you
#Points is list of structure which has x_coord, y_coord, isMax(if True then the node is Max node), level(Root at level 0)
#Edge List is the list of edges connecting the points mentioned above, you will need this when you have to color the edge for showing step by step representation
#Paths and Visited set is a dictionary, after each iteration in Paths insert the edge from the edge_list which you want to colour
#Visited is also a dictionary which will contain the index of the Point from list points

#Counter is the number of iterations it took, For eg: if counter is 5, you have to add your step by step solution in paths and visited_set as
#paths[0].....path[4] and visited_set[0]...visited[4]. This can be viewed as an animation in every mouse press event.

    #My code
    # Returns the max value for 2 numbers x and y
    def max(self,x,y):  
        if x > y :
            return x
        else :
            return y

    # Returns the min value for 2 numbers x and y
    def min(self,x,y) : 
        if x < y :
            return x
        else :
            return y

    # Returns number of the children for the desired node
    def getNumberOfChildren(self,edge_list,x,y) : 
        count=0
      #  print(" x: ",x,",y: ",y)
        for e in edge_list:
            if e[0][0]==x and e[0][1]==y :
                count=count+1

        return count

    # Returns the index of the first child of the desired internal node
    def getFirstChildIndex(self,x,y) :  

        #print("fcindex x: ",x,",y: ",y)
        for m in first_childs :
            #print(m[0][0],m[0][1], "-", m[1])
            if m[0][0]==x and m[0][1]==y:
                return m[1]

    # Returns the index of the points with co-ordinates x and y in the points list
    def getIndex(self,x,y):

        count=0
        for i in points:
            if i.x_coord==x and i.y_coord==y:
                return count
            else :
                count=count+1

    ### Calculates minimax values using alpha beta pruning from left to right
    def alphaBetaPruning(self, alpha, beta, depth, index):

        global visited_nodes

        visited_nodes.append(points[index])

        # print("now depth : ",depth)

        if depth==4 :
            # print("Reached leaf, value is ", points[index].value)
            return points[index].value

        if points[index].isMax== True:

            best=-infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
            # print("Max n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Max f c index:",f_child_index)
            for i in range(n) :
                
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.alphaBetaPruning(alpha,beta,depth+1,child_index);


                best=max(best,value)

               # points[child_index].value=best
                alpha=max(best,alpha)

                # print("Alpha now : ", alpha)
                # print("Beta now : ", beta)
                if beta <= alpha :
                    break
            
            points[index].value=best
            return best
        
        else :
            best = infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
            # print("Min n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Min f c index:",f_child_index)
            for i in range(n) :
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.alphaBetaPruning(alpha,beta,depth+1,child_index);

                best=min(best,value)

                #points[child_index].value=best
                beta=min(best, beta)

                # print("Alpha now : ", alpha)
                # print("Beta now : ", beta)

                if beta <= alpha :
                    break

            points[index].value=best
            return best

    ### Calculates minimax values using alpha beta pruning from right to left
    def alphaBetaPruningRL(self, alpha1, beta1, depth, index):

        # print("now depth : ",depth)

        if depth==4 :
            # print("Reached leaf, value is ", points[index].value)
            return points[index].value

        if points[index].isMax== True:

            best=-infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
            # print("Max n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Max f c index:",f_child_index)
            for i in range(n-1, -1, -1) :
                
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.alphaBetaPruningRL(alpha1,beta1,depth+1,child_index);

                best=max(best,value)

                #points[child_index].value=best
                alpha1=max(best,alpha1)

                # print("Alpha now : ", alpha)
                # print("Beta now : ", beta)
                if beta1 <= alpha1 :
                    break

            points[index].value=best
            return best
        
        else :
            best = infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
           # print("Min n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Min f c index:",f_child_index)
            for i in range(n-1,-1,-1) :
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.alphaBetaPruningRL(alpha1,beta1,depth+1,child_index);

                best=min(best,value)

                #points[child_index].value=best
                beta1=min(best, beta1)

                # print("Alpha now : ", alpha)
                # print("Beta now : ", beta)

                if beta1 <= alpha1 :
                    break

            points[index].value=best
            return best

    ### Calculates minimax values using minimax algorithm
    def runMinimax(self, depth, index):

        # print("now depth : ",depth)

        if depth==4 :
            # print("Reached leaf, value is ", points[index].value)
            return points[index].value

        if points[index].isMax== True:

            best=-infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
            # print("Max n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Max f c index:",f_child_index)
            for i in range(n) :
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.runMinimax(depth+1,child_index);

                best=max(best,value)

            return best
        
        else :

            best=infinity

            n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord);
           # print("Min n:",n)
            f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord);
            # print("Min f c index:",f_child_index)
            for i in range(n) :
                child=edge_list[f_child_index+i]
                # print("Child:", child)
                child_index=self.getIndex(child[1][0],child[1][1])
                value= self.runMinimax(depth+1,child_index);

                best=min(best,value)

            return best;

    # Trace the solution path from root to leaf
    def tracePath(self, index, value, depth): 

        global result_path
        found=False

        if depth==4 and points[index].value==value:
            return

        n=self.getNumberOfChildren(edge_list, points[index].x_coord, points[index].y_coord)

        f_child_index=self.getFirstChildIndex(points[index].x_coord, points[index].y_coord)

        for i in range(n) :
                
            child=edge_list[f_child_index+i]
            child_index=self.getIndex(child[1][0],child[1][1])

            if points[child_index].value==value and found==False :
                print(child)
                found=True
                result_path.append(child_index)
                self.tracePath(child_index,value,depth+1)

        return result_path
        


    def solution(self):
        global points
        global edge_list
        global levels
        global number_level_nodes
        global paths
        global visited_set
        global counter
        #global result_path
        global alpha
        global beta

        print("Write Your algorithm here, and print the final cost in console itself")

        setFirstChildIndexes(self,edge_list)
        
        counter=2
        minimax=self.alphaBetaPruning(alpha,beta,0,114)

        visited_set[counter]=visited_nodes
        

        print("The minimax value at the root by alpha beta pruning is :",minimax)

        minimax1=self.runMinimax(0,114)

        print("The minimax value at the root by minimax algorithm is :",minimax1)

        minimax2=self.alphaBetaPruningRL(alpha1,beta1,0,114)

        print("The minimax value at the root by alpha beta pruning from right to left is :",minimax2)

        print("The solution path is \n")
        result_path.append(114)
        solution_path=self.tracePath(114,minimax,0)

        paths[counter]=result_path

        # for i in points:
        #     print(i.x_coord,",",i.y_coord,"-",i.value)

        #Do not remove these lines
        #Keep them in the end of your program
        #Do not forget to update paths and visited_set
        self.event = "Display_Solution"
        self.update()

    def init_graph_paramaters(self):
        global points
        global edge_list
        global number_level_nodes
        global levels
        global result_path
        global paths
        global visited_set
        global iteration
        iteration = 0
        points = []
        edge_list = []
        number_level_nodes = []
        levels = 0
        result_path = []
        paths = dict()
        visited_set = dict()
        counter = 0

    def reset_screen(self):
        self.event = "Reset_Screen"
        self.update()

    def generateTree(self):
        self.event = "Generate_Tree"
        self.init_graph_paramaters()
        generate_points()
        generate_edges()
        self.update()

    def saveTree(self):
        global points
        global edge_list
        global number_level_nodes

        with open('Treepoints.pkl', 'wb') as f:
            pickle.dump(points, f)

        with open('Treeedge_list.pkl', 'wb') as f:
            pickle.dump(edge_list, f)

        with open('Treenumber_list.pkl', 'wb') as f:
            pickle.dump(number_level_nodes, f)

        self.update()

    def loadTree(self):
        global points
        global edge_list
        global levels
        global number_level_nodes
        global node_colour
        global paths
        global counter
        global iteration
        global result_path
        global visited_set

        with open('Treepoints.pkl', 'rb') as f:
            points = pickle.load(f)

        with open('Treeedge_list.pkl', 'rb') as f:
            edge_list = pickle.load(f)

        with open('Treenumber_list.pkl', 'rb') as f:
            number_level_nodes = pickle.load(f)

        node_colour = [0 for p in points]
        paths = dict()
        visited_set = dict()
        counter = 0
        iteration = 0
        result_path = []

        self.event = "Generate_Tree"
        self.update()


    def initUI(self):

        self.saveAct = QAction('&Save Tree', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save Tree')
        self.saveAct.triggered.connect(self.saveTree)

        self.loadAct = QAction('&Load Tree', self)
        self.loadAct.setShortcut('Ctrl+O')
        self.loadAct.setStatusTip('Load Tree')
        self.loadAct.triggered.connect(self.loadTree)

        self.genTreeAct = QAction('&Generate Tree', self)
        self.genTreeAct.triggered.connect(self.generateTree)

        self.solveAlgoAct = QAction('&Algorithm', self)
        self.solveAlgoAct.triggered.connect(self.solution)

        self.resetAct = QAction('&Reset Screen', self)
        self.resetAct.triggered.connect(self.reset_screen)

        self.exitAct = QAction('&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(qApp.quit)

        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.loadAct)
        self.fileMenu.addAction(self.exitAct)

        self.toolbar = self.addToolBar('')
        self.toolbar.addAction(self.genTreeAct)
        self.toolbar.addAction(self.solveAlgoAct)
        self.toolbar.addAction(self.resetAct)

        self.setMouseTracking(True)
        self.solveAlgoAct.setEnabled(False)


    def __init__(self):
        super().__init__()

        self.nodes = -1
        self.bf = -1
        self.dict_index_coord = {}
        self.open_list = []
        self.closed_list = []
        self.leaf_values = []
        self.event = -1

        self.initUI()
        self.setMinimumSize(QSize(screen_width, screen_height))
        self.setWindowTitle("TreePlatform")


    #After every mouse press event on screen this function is called
    def mousePressEvent(self):
        global iteration
        global counter
        global result_path
        global paths
        global node_colour
        global visited_set

        if self.event == "Display_Solution":
            iteration += 1
            if iteration < counter:
                visited = visited_set[iteration]
                result_path = paths[iteration]
                for j in visited:
                    node_colour[j] = 1  ##Magenta
            else:
                print("Program Completed")


    #This function is called continously after some time intervals by python program
    #Understand this function for better understanding of your assignment and what is expected.
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        global points
        global node_colour

        qp.setPen(Qt.red)
        if self.event == "Generate_Tree":
            qp.setBrush(Qt.yellow)
            for point in points:
                if point.isMax:
                    qp.drawRect(point.x_coord, point.y_coord, 15, 15)
                else:
                    center = QPoint(point.x_coord, point.y_coord)
                    qp.drawEllipse(center, 8, 8)

            self.drawLine(qp)
            self.solveAlgoAct.setEnabled(True)

        elif self.event == "Display_Solution":
            for index in range(len(points)):
                e = node_colour[index]
                if e == 0:
                    qp.setBrush(Qt.yellow)
                elif e == 1:
                    qp.setBrush(Qt.magenta)
                elif e == 2:
                    qp.setBrush(Qt.blue)
                elif e == 3:
                    qp.setBrush(Qt.cyan)
                elif e == 4:
                    qp.setBrush(Qt.red)

                point = points[index]
                if point.isMax:
                    qp.drawRect(point.x_coord, point.y_coord, 15, 15)
                else:
                    center = QPoint(point.x_coord, point.y_coord)
                    qp.drawEllipse(center, 8, 8)
            self.drawLine(qp)


    def drawLine(self, qp):
        global edge_list
        global result_path

        pen = QPen(Qt.black, 1, Qt.DashDotDotLine)
        qp.setPen(pen)
        for e in edge_list:
            qp.drawLine(e[0][0], e[0][1], e[1][0], e[1][1])

        if len(result_path) != 0:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            qp.setPen(pen)
            for i in range(0, len(result_path) - 1, 1):
                prev_point = points[result_path[i]]
                next_point = points[result_path[i+1]]
                qp.drawLine(prev_point.x_coord, prev_point.y_coord, next_point.x_coord, next_point.y_coord)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = Tree()
    tree.show()
    sys.exit(app.exec_())
