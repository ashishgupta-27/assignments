import xml.etree.ElementTree as ET
import os


#Update the path which will be the working directory before invoking the command to generate XML from FOL formulas
directory_path="<UPDATE_PATH_HERE>"
#Give only the name of input file
kb_file="fchain-kb"
query_file='fchain-query'
#Update the path where the KRR.jar and antlr.jar is available
utility_jar_path="<UPDATE_PATH_HERE>"
os.chdir(directory_path)

kb_cmd=r'java -cp "'+utility_jar_path+r'KRR.jar;'+utility_jar_path+r'lib\\antlr-3.5.2-complete.jar" krr.main.Tool -FOL input\\'+kb_file+r'.txt 1>output\\'+kb_file+r'-out.xml 2>output\\'+kb_file+r'-err.txt'

q_cmd=r'java -cp "'+utility_jar_path+r'KRR.jar;'+utility_jar_path+r'lib\\antlr-3.5.2-complete.jar" krr.main.Tool -FOL input\\'+query_file+r'.txt 1>output\\'+query_file+r'-out.xml 2>output\\'+query_file+r'-err.txt'

print('Converting FOL formulas from text to XML')
print('Running command:'+kb_cmd)
os.system(kb_cmd)

print('Running command:'+q_cmd)
os.system(q_cmd)

#Loading the KB XML
output_file_path=directory_path+r'\\output\\'+kb_file+r'-out.xml'
tree = ET.parse(output_file_path)
root = tree.getroot()

# Loading the query XML
qout_file_path=directory_path+r'\\output\\'+query_file+r'-out.xml'
q_tree = ET.parse(qout_file_path)
q_root = tree.getroot()

# Loading of rules of inferences
rules_file_path=directory_path+r'\\output\\rules-out.xml'
rules_tree=ET.parse(rules_file_path)
rules_root=rules_tree.getroot()

#Stores the knowledge base as a list
kb=list()
for child in root:
    kb.append(child)
    #print('Node:')
    #ET.dump(child)

left_child=root[0]
right_child=root[1]
global theta_list
theta_list=[]

#Checks the occurence of a variable in the substitution list as well as in the nested XML subelements
def occur_check(var, child, theta_list):

    for subchild in child.iter('VARIABLE'):
        x=subchild.attrib.get('text')
        for theta in theta_list:

            if(var==x):
                return True
            elif(var in theta):
                return True
            else:
                return False

#Returns the substitution value given a variable and substitution list
def get_substitution_value(theta_list,x):

    result=''
    for theta in theta_list:
        if(x in theta):
            result=theta.split("/",1)[1] 
            break

    return result

#Compares the node elements if both of them are functions
def func_check(left_child,right_child,theta_list):
    left_child_value=left_child.attrib.get('text')
    right_child_value=right_child.attrib.get('text')

    if(left_child.tag=='CONSTANT' and right_child.tag=='CONSTANT'):
        if(left_child_value!=right_child_value):
            return 'UNIFICATION FAILED'
    elif(left_child.tag=='VARIABLE' and right_child.tag=='VARIABLE'):
        if(left_child_value!=right_child_value):
            left_sub_value=get_substitution_value(theta_list,left_child_value)
            right_sub_value=get_substitution_value(theta_list,right_child_value)
            if(left_sub_value=='' and right_sub_value!=''):
                theta=left_child_value+'/'+right_sub_value
                theta_list.append(theta)
                return theta_list
            elif(right_sub_value=='' and left_sub_value!=''):
                theta=right_child_value+'/'+left_sub_value
                theta_list.append(theta)
                return theta_list
            elif(left_sub_value!=right_sub_value):
                return 'UNIFICATION FAILED'
    elif(left_child.tag=='VARIABLE' and right_child.tag=='CONSTANT'):
        left_sub_value=get_substitution_value(theta_list,left_child_value)
        if(left_sub_value==''):
            theta=left_child_value+'/'+right_child_value
            theta_list.append(theta)
            return theta_list
        elif(left_sub_value!=right_child_value):
            return 'UNIFICATION FAILED'
    elif(right_child.tag=='VARIABLE' and left_child.tag=='CONSTANT'):
        right_sub_value=get_substitution_value(theta_list,right_child_value)
        if(right_sub_value==''):
            theta=right_child_value+'/'+left_child_value
            theta_list.append(theta)
            return theta_list
        elif(right_sub_value!=left_child_value):
            return 'UNIFICATION FAILED'

    return theta_list

#Unification algorithm implementation
def unify(left_child, right_child, theta_list):


    if(left_child.tag=='PREDICATE' and right_child.tag=='PREDICATE'):

        left_child_predicate=left_child.attrib.get('text')
        right_child_predicate=right_child.attrib.get('text')

        if(left_child_predicate!=right_child_predicate):
            return "UNIFICATION FAILED"

        elif(len(list(left_child))!=len(list(right_child))) :
            return "UNIFICATION FAILED"

    if (left_child.tag=='CONSTANT' and right_child.tag=='CONSTANT'):
        #print('In constant')
        left_constant=left_child.attrib.get('text')
        right_constant=right_child.attrib.get('text')
        if(left_constant==right_constant):
            return theta_list
        else:
            return 'UNIFICATION FAILED'

    elif (left_child.tag=='VARIABLE' and right_child.tag=='VARIABLE'):
        #print('In variable')
        left_variable=left_child.attrib.get('text')
        right_variable=right_child.attrib.get('text')
        if(left_variable==right_variable):
            return theta_list
        else:
            left_sub_value=get_substitution_value(theta_list,left_variable)
            right_sub_value=get_substitution_value(theta_list,right_variable)
            if(left_sub_value!=right_sub_value):
                return 'UNIFICATION FAILED'

    elif(left_child.tag=='VARIABLE' and (right_child.tag=='CONSTANT' or right_child.tag=='FUNCTION')):

        left_child_value=left_child.attrib.get('text')
        right_child_value=''
        if(right_child.tag=='CONSTANT'):
            left_sub_value=get_substitution_value(theta_list,left_child_value)
            right_child_value=right_child.attrib.get('text')
            if(left_sub_value!='' and left_sub_value!=right_child_value):
                return 'UNIFICATION FAILED'
        elif(right_child.tag=='FUNCTION'):
            if(occur_check(left_child_value,right_child,theta_list)):
                return 'UNIFICATION FAILED'
            else:
                right_child_value=right_child.attrib.get('text')
                arg_list=[]
                for subchild in right_child:
                    if(subchild.tag=='VARIABLE'):
                        subchild_sub_value=get_substitution_value(theta_list,subchild.attrib.get('text'))
                        if(subchild_sub_value==''):
                            return 'UNIFICATION FAILED'
                        else:
                            arg_list.append(subchild_sub_value)
                    else:
                        arg_list.append(subchild.attrib.get('text'))
                arg_list_str= ','.join(arg_list)
                right_child_value=right_child_value+'('+arg_list_str+')'

        theta=left_child_value+'/'+right_child_value
   
        if(right_child_value!='' and theta not in theta_list):        
            theta_list.append(theta)

        #print('IN V/C:',theta_list)
        return theta_list

    elif(right_child.tag=='VARIABLE' and (left_child.tag=='CONSTANT' or left_child.tag=='FUNCTION')):

        right_child_value=right_child.attrib.get('text')
        left_child_value=''
        if(left_child.tag=='CONSTANT'):
            right_sub_value=get_substitution_value(theta_list,right_child_value)
            left_child_value=left_child.attrib.get('text')
            if(right_sub_value!='' and right_sub_value!=right_child_value):
                return 'UNIFICATION FAILED'
        elif(left_child.tag=='FUNCTION'):
            if(occur_check(right_child_value,left_child,theta_list)):
                return 'UNIFICATION FAILED'
            else:
                left_child_value=left_child.attrib.get('text')
                arg_list=[]
                for subchild in left_child:
                    if(subchild.tag=='VARIABLE'):
                        subchild_sub_value=get_substitution_value(theta_list,subchild.attrib.get('text'))
                        if(subchild_sub_value==''):
                            return 'UNIFICATION FAILED'
                        else:
                            arg_list.append(subchild_sub_value)
                    else:
                        arg_list.append(subchild.attrib.get('text'))
                arg_list_str= ','.join(arg_list)
                left_child_value=left_child_value+'('+arg_list_str+')'

        theta=right_child_value+'/'+left_child_value
        if(left_child_value!='' and theta not in theta_list):
            theta_list.append(theta)
        
        return theta_list

    elif (left_child.tag=='FUNCTION' and right_child.tag=='FUNCTION'):
        if(left_child.attrib.get('text')!=right_child.attrib.get('text')):
            return 'UNIFICATION FAILED'
        elif(len(list(left_child))!=len(list(right_child))):
            return 'UNIFICATION FAILED'
        else :
            length=len(list(left_child))
            for i in range(length):
                sub_left_child=left_child[i]
                sub_right_child=right_child[i]
                theta_list=func_check(sub_left_child,sub_right_child,theta_list)
        
        return theta_list
               
    else:
        length=len(list(left_child))
        #print(length)
        if(length > 0) :
            for i in range(length):
                sub_left_child=left_child[i]
                sub_right_child=right_child[i]
                theta_list=unify(sub_left_child,sub_right_child,theta_list)
        
        return theta_list
       
result=unify(left_child,right_child,theta_list)

def get_consequent(node):

    if(node.tag=='IMPLIES'):
        return node[0]
    
    return None

def get_eng_pred(node):

        result=''

    #if(node.tag=='PREDICATE'):
        result=node.attrib.get('text')
        var_list=list()
        for child in node:
            var_list.append(child.attrib.get('text'))
            
        var_list_str=','.join(var_list)
        result=result+'('+var_list_str+')'
    
        return result

def get_eng_compound(node):

    result=''

    if(node.tag=='IMPLIES' or node.tag=='OR' or node.tag=='AND'):
        connective=node.tag.lower()
        pred1=get_eng_pred(node[0])
        pred2=get_eng_pred(node[1])

        result=pred1+" "+connective+" "+pred2
    else:
        result=get_eng_pred(node)

    return result

def substitute_value(result,theta_list):

    length=len(result)
    for i in range(length):
        if(result[i].isupper()):

            for theta in theta_list:
                if(result[i] in theta):
                    value=theta.split("/",1)[1] 
                    break
            result=result.replace(result[i],value)

    return result


def match_pred(pred1,pred2):
   # ET.dump(pred1)
    #ET.dump(pred2)
    if(len(pred1)!=len(pred2)):
        return False
    elif(pred1.tag!=pred2.tag):
        return False
    else:
        length=len(pred1)
        for i in range(length):
            if(pred1[i].tag=='CONSTANT' and pred2[i].tag=='VARIABLE'):
                continue
    
    return True

def match_implication(pred1,pred2):
    if(len(pred1)!=len(pred2)):
        return False
    elif(pred1.tag!=pred2.tag):
        return False
    else:
        length=len(pred1)
        for i in range(length):
            if(match_pred(pred1[i],pred2[i]) == False):
                return False
    
    return True

def match_rule(pred1,pred2,rule):

    rule_condition=rule[0]
    rule_action=rule[1]
    #print('Ac:')
    #ET.dump(rule_action)
    #ET.dump(pred2[1])
    if(match_pred(pred1,rule_condition[0]) and match_implication(pred2, rule_condition[1])):
        return pred2[1]
    else:
        return False

def match_query(action,query,theta_list):
    #ET.dump(action)
    #ET.dump(query)
    if(len(action)!=len(query)):
        return False
    elif(action.tag!=query.tag):
        return False
    elif(match_pred(action,query)==False):
        return False
    else:
        query_str=get_eng_pred(query)
        query_str=substitute_value(query_str,theta_list)

        return query_str


def forward_chain(kb):
    length=len(kb)
    for i in range(length):
        for j in range(i+1,length):

            node1=kb[i]
            node2=kb[j]
            result=''
            if(node1.tag=='IMPLIES'):
                consequent_node=get_consequent(node1)
                result=unify(node2,consequent_node,theta_list)
            elif(node2.tag=='IMPLIES'):
                consequent_node=get_consequent(node2)
                result=unify(node1,consequent_node,theta_list)


            node1_str=get_eng_compound(node1)
            node2_str=get_eng_compound (node2)
            #print('FOL1:',node1_str)
            #print('FOL2:',node2_str) 
            i=1          
            if(type(result) is list):
                #print('UNIFICATION SUCCESSFUL.The substitution list :',result)
                print(i,'.',node1_str, '\t ...Premise')
                i=i+1
                print(i,'.',node2_str, '\t ...Premise')
                i=i+1
                unified_str=substitute_value(node2_str,result)
                print(i,'.',unified_str,'\t ...Unification of',i-2, 'and', i-1)
                i=i+1
                if(match_rule(node1,node2,rules_root[0])!=False):

                    action=match_rule(node1,node2,rules_root[0])
                    #ET.dump(action)
                    if(match_query(q_root[0],action,theta_list)!=False):
                        query_str=match_query(q_root[0],action,theta_list)
                        print(i,'.',query_str,'\t ...Modus Ponens rule')

            elif(result=='UNIFICATION FAILED'):
                print('FALSE')

forward_chain(kb)




