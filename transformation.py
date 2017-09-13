# -*- coding: utf-8 -*-
"""
Transforms RDf data structured in a data model, to other data model, according to the mapping provided as input

Python ver: 3.5
"""

from rdflib.util import guess_format
from rdflib import Graph, URIRef
from rdflib.namespace import SKOS, RDF
import sys

input_file = sys.argv[1]
mapping_file = sys.argv[2]
output_file = sys.argv[3]
input_format = guess_format(input_file)
output_format = guess_format(output_file)

g_input = Graph ()
g_mapping = Graph ()
g_output = Graph ()
g_mapping.parse (mapping_file)
g_input.parse (input_file, format=input_format)

type_matches = ["mappingRelation", "closeMatch", "exactMatch", "broadMatch", "narrowMatch", "relatedMatch"]

#Process all the classes from the input file
for si,pi,oi in g_input.triples ( (None, RDF.type, None) ):
	#Check all the different types of matches at classes level
	for match in type_matches:
		#Check if there is any match of the source class. The result is the URI of the target class
		get_target_class = "select ?class where { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#mappingRelation>; <http://www.w3.org/2000/01/rdf-schema#Class> <"+ str(oi) +">; <http://www.w3.org/2004/02/skos/core#"+match+"> ?class. FILTER (!EXISTS {?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> ?prop })} "
		res = g_mapping.query(get_target_class)
		
		for row in res:
			#Create the new triple with the new class URI
			g_output.add ( (si, RDF.type, row[0] ) )
			
			#If there is a match at the class level, look for property matches
			
			for s,p,o in g_input.triples ( (si, None, None) ):
				if p != RDF.type:
					get_target_property = "select ?prop where { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#mappingRelation>; <http://www.w3.org/2000/01/rdf-schema#Class> <"+ str(oi) +">; <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> <"+ str(p) +">; <http://www.w3.org/2004/02/skos/core#exactMatch> ?prop; <http://www.w3.org/2004/02/skos/core#inScheme> <"+str(row[0])+"> }"
					res_prop = g_mapping.query(get_target_property)
					
					#Add the transformed triple. The subject is the original one (si), the predicate is the target property obtained from the query and the object the object of the source triple (o)
					for row_prop in res_prop:
						g_output.add ( (si, row_prop[0], o ) )
			
		
output = open(output_file, "w")
g_output.serialize(destination=output_file, format=output_format)

# Cleanup the graph instance
g_input.close()
g_mapping.close()


