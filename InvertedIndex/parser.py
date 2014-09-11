import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lexer import tokens
from evaluate_query_without_db import score_entry,plentry,query_evaluation
no_of_documents=800
temp_class=-1
class MyParser:
	def __init__(self):
		self.tokens=tokens
		self.parser=yacc.yacc(module=self)
		self.temp_class=query_evaluation("document.pickle","dictionary.pickle","posting_list")
	def p_expression_or(self,p):
		'''start_expression : start_expression OR expression1 
							| expression1'''
		if(len(p)==4):
			dic_if_id_present={}
			ans_list=[]
			for i in range(len(p[1])):
				dic_if_id_present[p[1][i].doc_id]=p[1][i].score
			for i in range(len(p[3])):
				if(dic_if_id_present.has_key(p[3][i].doc_id)):
					ans_list.append(score_entry(p[3][i].doc_id , p[3][i].score+dic_if_id_present[p[3][i].doc_id]))
				else :
					ans_list.append(p[3][i])
			p[0]=sorted(ans_list, key=lambda x: x.score)
		else:
			p[0]=p[1]

	def p_expression_and(self,p):
		'''expression1  : expression1 AND expression 
						| expression'''
		if(len(p)==4):
			dic_if_id_present={}
			ans_list=[]
			for i in range(len(p[1])):
				dic_if_id_present[p[1][i].doc_id]=p[1][i].score
			for i in range(len(p[3])):
				if(dic_if_id_present.has_key(p[3][i].doc_id)):
					ans_list.append(score_entry(p[3][i].doc_id , p[3][i].score+dic_if_id_present[p[3][i].doc_id]))
			p[0]=sorted(ans_list, key=lambda x: x.score)
		else:
			p[0]=p[1]

	def p_expression_not(self,p):
		'''expression   : NOT start_expression 
						| query 
						| LPAREN start_expression RPAREN'''
		if(p[1]=='!'):
			dic_if_id_present={}
			ans_list=[]
			for i in range(len(p[2])):
				dic_if_id_present[p[2][i].doc_id]=p[2][i].score
			for i in range(no_of_documents):
				if(dic_if_id_present.has_key(i)):
					ans_list.append(scoreEntry(i,-dic_if_id_present[i]))
				else:
					ans_list.append(score_entry(i,0))
			p[0]=sorted(ans_list, key=lambda x: x.score)
		elif(p[1]=='('):
			p[0]=p[2]
		else:
			p[0]=p[1]

	def p_expression_query(self,p):
		'''query    : QUOTES TERMS QUOTES 
					| TERMS'''
		if(p[1]=='"'):
			term_list=[]
			for i in p[2].split():
				if(i!=' '):
					term_list.append(i)
			ans_list=self.temp_class.phrasalquery(term_list,0)
			p[0]=sorted(ans_list, key=lambda x: x.score)
		else:
			term_list=[]
			for i in p[1].split():
				if(i!=' '):
					term_list.append(i)
			print term_list
			ans_list=self.temp_class.multiquery(term_list,0)
			p[0]=sorted(ans_list, key=lambda x: x.score)
			#print p[0]
	def test(self,input):
		result=self.parser.parse(input)
		return result