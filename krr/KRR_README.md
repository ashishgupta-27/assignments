KRR text to XML parser
Steps to be followed to parse a text file (as per language specification document) and convert to XML file:

1. Download and extract the KRR package from the given dropbox link.
2. Change your working directory to /KRR/src/krr/test
3. Put your text file in /KRR/src/krr/test/input
4. (Edit commands and) run r.sh file
5. Find the generated XML file in /KRR/src/krr/test/output

For example: 

If the input file has FOL formulas and it is named test-krr.txt, then r.sh file should have the following commands:

JARDIR="../../.."

KRRRT="$JARDIR/dist/KRR.jar:$JARDIR/lib/antlr-3.5.2-complete.jar"

java -cp $KRRRT krr.main.Tool -FOL   input/test-krr.txt  1>output/test-krr-out.xml  2>output/test-krr-err.txt


The sample input and output files available at /KRR/src/krr/test/input and /KRR/src/krr/test/output folders respectively.


Note: 
1. The KRR and antlr jar files provided in the package (as used in the above commands) are sufficient to convert text files (in the specified grammar) to XML notation. The above package has been released with the source files just for learning purposes.

2. It uses ANTLR to generate lexers and parsers for the different languages whose grammar is specified in '*.g' files in KRR/src/in/ac/iitm/cse/parser/* directories. More about ANTLR. 