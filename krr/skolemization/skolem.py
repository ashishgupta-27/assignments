import xml.etree.ElementTree as ET
#from lxml import ET
import os


#Update the path which will be the working directory before invoking the command to generate XML from FOL formulas
directory_path="<UPDATE_PATH_HERE>"
#Give only the name of input file
input_file="demo"
#Update the path where the KRR.jar and antlr.jar is available
utility_jar_path="<UPDATE_PATH_HERE>"
os.chdir(directory_path)
cmd=r'java -cp "'+utility_jar_path+r'KRR.jar;'+utility_jar_path+r'lib\\antlr-3.5.2-complete.jar" krr.main.Tool -FOL input\\'+input_file+r'.txt 1>output\\'+input_file+r'-out.xml 2>output\\'+input_file+r'-err.txt'

print('Converting FOL formulas from text to XML')
print('Running command:'+cmd)
os.system(cmd)

output_dir="<UPDATE_PATH_HERE>" #Output directory path

tree = ET.parse(output_dir+input_file+"-out.xml")
root = tree.getroot()

new_root = ET.Element(root.tag)
new_tree = ET.ElementTree(new_root) #to copy the tags to new XML file without quantifiers

# Gets the variable list for a quantifier
def get_var_list(node):

    var_list=[]
    for child in node:
        #print(subchild.tag, subchild.attrib)
        if(child.tag == 'VARIABLE'):
            variable=child.attrib.get('text')
            if('?' not in variable):
                var_list.append(variable)
        elif(child.tag =='VARLIST'):
            for subchild in child:
                variable=subchild.attrib.get('text')
                if('?' not in variable):
                    var_list.append(variable)

    return var_list

## Sets the skolem function for existential quantifier occuring on the right of universal quantifier
def set_skolem_func(node, var_list):
    univ_var_list_str= ',?'.join(var_list)
    univ_var_list_str='?'+univ_var_list_str

    for child in node.findall('EXISTS'):

        print(child.tag, child.attrib)
        exists_var_list=get_var_list(child)

        for subchild in child.iter('VARIABLE'):
            print (subchild.tag, subchild.attrib)
            variable=subchild.attrib.get('text')
            if(variable in exists_var_list):
                subchild.set('text',variable+'SK('+univ_var_list_str+')')
        

## Replace all universal quantifier variables (say X) with ?X
def univ_skolemization(root) :
    for child in root.iter('FORALL'):
        univ_var_list=get_var_list(child)
        #print(child.tag, child.attrib)
        print("Universally quantified variables list:")
        print(univ_var_list)
            
        for subchild in child.iter('VARIABLE'):
                    
            variable=subchild.attrib.get('text')
            if(variable in univ_var_list):
                subchild.set('text','?'+variable)
                print (subchild.tag, subchild.attrib)

        set_skolem_func(child,univ_var_list)

## Handles the exception case of existential quantifier implication case
def exception_case(node,var_list):
    if (node[1].tag == 'IMPLIES'):
        children=list(node[1])
        left_child=children[0]
        right_child=children[1]
        var_in_left=False 
        for child in left_child:
            if(child.tag == 'VARIABLE'):
                variable=child.attrib.get('text')
                if (variable in var_list):
                    var_in_left=True
                    child.set('text','?'+variable)
            elif(child.tag =='VARLIST'):
                for subchild in child:
                    variable=subchild.attrib.get('text')
                    if(variable in var_list):
                        var_in_left=True
                        subchild.set('text','?'+variable)

        if(var_in_left == True):
            for child in right_child:
                if(child.tag == 'VARIABLE'):
                    variable=child.attrib.get('text')
                    if (variable in var_list):
                        var_in_left=True
                        child.set('text','?'+variable)
                elif(child.tag =='VARLIST'):
                    for subchild in child:
                        variable=subchild.attrib.get('text')
                        if(variable in var_list):
                            var_in_left=True
                            subchild.set('text','?'+variable)


## Replace all existential quantifier variables (say X) without any universal quantifiers to its left with XSK
def set_skolem_const(root):
    for child in root.findall('EXISTS'):

        print(child.tag, child.attrib)
        exists_var_list=get_var_list(child)
        exception_case(child,exists_var_list)

        for subchild in child.iter('VARIABLE'):
            variable=subchild.attrib.get('text')
            if(variable in exists_var_list and '?' not in variable):
                subchild.set('text',variable+'SK')
                print (subchild.tag, subchild.attrib)
    
    univ_skolemization(child)


## Remove all quantifier and its variable tags
def create_new_xml(root):

    
    for child in root:
        if(child.tag == 'EXISTS' or child.tag == 'FORALL'):
            for subchild in child:
                if(subchild.tag != 'VARIABLE' and subchild.tag != 'VARLIST' ):
                # ET.SubElement(new_root,subchild);
                    if(subchild.tag=='EXISTS' or subchild.tag=='FORALL'):
                        for subsubchild in subchild:
                             if(subsubchild.tag != 'VARIABLE' and subsubchild.tag != 'VARLIST' ):
                                 new_root.append(subsubchild)
                    else :
                        new_root.append(subchild)
                    
                    print (subchild.tag, subchild.attrib)

                    #root.remove(subchild);
                # root.remove(child);
        else :
            new_root.append(child)

    new_tree.write(output_dir+"sou_new.xml")


def sk_update():
    utree = ET.parse(output_dir+"sou_new.xml")
    root = utree.getroot()

    for child in root.iter('VARIABLE'):

        text=child.attrib.get('text')
        print('Text : ',text)
        if(not(type(text) is None) and 'SK(' in text):
            child.tag="FUNCTION"
            
            r1=text.split("(",1)
            child.set('text', r1[0])
            v1=r1[1]

            for i in range(len(v1)):
                if('?' in v1[i]):
                    print('Inserting : ',v1[i]+v1[i+1])
                    uni_var = ET.Element('VARIABLE')
                    uni_var.set('text',v1[i]+v1[i+1])
                    #abc.text=v1[i]+v1[i+1]
                    child.insert(1,uni_var)
                    i=i+1
            #child.insert()
            print('Function')

        elif('SK' in child.attrib.get('text')):
            child.tag="CONSTANT"
            print('Constant')

    utree.write(output_dir+"final_sout.xml")

    print("Skolemization complete")



univ_skolemization(root)
set_skolem_const(root)
tree.write(output_dir+'sout.xml')
create_new_xml(root)
sk_update()