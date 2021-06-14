import xml.etree.ElementTree as ET
import os


#Update the path which will be the working directory before invoking the command to generate XML from FOL formulas
directory_path="<UPDATE_PATH_HERE>"
#Give only the name of input file
input_file="unify3"
#Update the path where the KRR.jar and antlr.jar is available
utility_jar_path="<UPDATE_PATH_HERE>"
os.chdir(directory_path)
cmd=r'java -cp "'+utility_jar_path+r'KRR.jar;'+utility_jar_path+r'lib\\antlr-3.5.2-complete.jar" krr.main.Tool -FOL input\\'+input_file+r'.txt 1>output\\'+input_file+r'-out.xml 2>output\\'+input_file+r'-err.txt'

print('Converting FOL formulas from text to XML')
print('Running command:'+cmd)
os.system(cmd)

output_file_path=directory_path+r'\\output\\'+input_file+r'-out.xml'
tree = ET.parse(output_file_path)
root = tree.getroot()

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
    #print('Get sub value list:',theta_list)
    #print('Get sub value variable:',x)
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
            elif(left_sub_value=='' and right_sub_value==''):
                theta=left_child_value+'/'+right_child_value
                #print(theta)
                theta_list.append(theta)
                return theta_list
            elif(left_sub_value!=right_sub_value):
                return 'UNIFICATION FAILED'
    elif(left_child.tag=='VARIABLE' and right_child.tag=='CONSTANT'):
        left_sub_value=get_substitution_value(theta_list,left_child_value)
        #print('In FF VC value:',left_sub_value)
        if(left_sub_value==''):
            theta=left_child_value+'/'+right_child_value
            theta_list.append(theta)
            return theta_list
        elif(left_sub_value!=right_child_value):
            return 'UNIFICATION FAILED'
    elif(right_child.tag=='VARIABLE' and left_child.tag=='CONSTANT'):
        right_sub_value=get_substitution_value(theta_list,right_child_value)
        #print('In FF CV sub value:',right_sub_value)
        if(right_sub_value==''):
            theta=right_child_value+'/'+left_child_value
            theta_list.append(theta)
            return theta_list
        elif(right_sub_value!=left_child_value):
            return 'UNIFICATION FAILED'

    return theta_list

# ET.dump(left_child)
# ET.dump(right_child)
#Unification algorithm implementation
def unify(left_child, right_child, theta_list):


    if(left_child.tag=='PREDICATE' and right_child.tag=='PREDICATE'):

        left_child_predicate=left_child.attrib.get('text')
        right_child_predicate=right_child.attrib.get('text')

        #print(left_child_predicate+" "+right_child_predicate)
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
            #print(left_sub_value,right_sub_value)
            if(left_sub_value=='' and right_sub_value==''):
                theta=left_variable+'/'+right_variable
                #print(theta)
                theta_list.append(theta)
                return theta_list
            elif(left_sub_value!=right_sub_value):
                return 'UNIFICATION FAILED'

    elif(left_child.tag=='VARIABLE' and (right_child.tag=='CONSTANT' or right_child.tag=='FUNCTION')):
        #print('In left variable and/or right constant')
        #print(left_child.tag, left_child.attrib)
        #print(right_child.tag, right_child.attrib)
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
        #print(theta)   
        #print(theta_list)     
        if(right_child_value!='' and theta not in theta_list):        
            #print(theta)
            theta_list.append(theta)

        #print('IN V/C:',theta_list)
        return theta_list

    elif(right_child.tag=='VARIABLE' and (left_child.tag=='CONSTANT' or left_child.tag=='FUNCTION')):
        #print('In right variable and/or left constant')
        #print(left_child.tag, left_child.attrib)
        #print(right_child.tag, right_child.attrib)
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
            #print(theta)
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
                #print('In else:', sub_left_child.tag,sub_left_child.attrib)
                #print('In else:', sub_right_child.tag,sub_right_child.attrib)
                #print('In else:', theta_list)
                theta_list=unify(sub_left_child,sub_right_child,theta_list)
                #print('In else after:', theta_list)
        
        return theta_list
       
result=unify(left_child,right_child,theta_list)
if(type(result) is list):
    print('UNIFICATION SUCCESSFUL.The substitution list :',result)
else:
    print(result)
