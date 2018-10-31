# -*- encoding:utf-8 -*-
#
# $Id$
#
from flask import current_app
from .sphinxapi3 import *
import sys, time, json

# if not sys.argv[1:]:
# 	print("Usage: python test.py [OPTIONS] query words\n")
# 	print("Options are:")
# 	print("-h, --host <HOST>\tconnect to searchd at host HOST")
# 	print("-p, --port\t\tconnect to searchd at port PORT")
# 	print("-i, --index <IDX>\tsearch through index(es) specified by IDX")
# 	print("-s, --sortby <EXPR>\tsort matches by 'EXPR'")
# 	print("-a, --any\t\tuse 'match any word' matching mode")
# 	print("-b, --boolean\t\tuse 'boolean query' matching mode")
# 	print("-e, --extended\t\tuse 'extended query' matching mode")
# 	print("-f, --filter <ATTR>\tfilter by attribute 'ATTR' (default is 'group_id')")
# 	print("-v, --value <VAL>\tadd VAL to allowed 'group_id' values list")
# 	print("-g, --groupby <EXPR>\tgroup matches by 'EXPR'")
# 	print("-gs,--groupsort <EXPR>\tsort groups by 'EXPR'")
# 	print("-l, --limit <COUNT>\tretrieve COUNT matches (default is 20)")
# 	sys.exit(0)

q = ''
mode = SPH_MATCH_ALL

index = '*'
filtercol = 'group_id'
filtervals = []
sortby = ''
groupby = ''
groupsort = '@group desc'
limit = 0

i = 1
while (i<len(sys.argv)):
	arg = sys.argv[i]
	if arg=='-h' or arg=='--host':
		i += 1
		host = sys.argv[i]
	elif arg=='-p' or arg=='--port':
		i += 1
		port = int(sys.argv[i])
	elif arg=='-i':
		i += 1
		index = sys.argv[i]
	elif arg=='-s':
		i += 1
		sortby = sys.argv[i]
	elif arg=='-a' or arg=='--any':
		mode = SPH_MATCH_ANY
	elif arg=='-b' or arg=='--boolean':
		mode = SPH_MATCH_BOOLEAN
	elif arg=='-e' or arg=='--extended':
		mode = SPH_MATCH_EXTENDED
	elif arg=='-f' or arg=='--filter':
		i += 1
		filtercol = sys.argv[i]
	elif arg=='-v' or arg=='--value':
		i += 1
		filtervals.append ( int(sys.argv[i]) )
	elif arg=='-g' or arg=='--groupby':
		i += 1
		groupby = sys.argv[i]
	elif arg=='-gs' or arg=='--groupsort':
		i += 1
		groupsort = sys.argv[i]
	elif arg=='-l' or arg=='--limit':
		i += 1
		limit = int(sys.argv[i])
	else:
		# q = '%s%s' % ( q, arg )
		q = ""
		# q = '@title 比特币'
	i += 1



def query_keyword(index, q, host, port):

	host = host
	port = port
	# do query
	cl = SphinxClient()
	cl.SetServer(host, port)
	# cl.SetMatchMode ( mode )
	cl.SetMatchMode(SPH_MATCH_EXTENDED)

	if filtervals:
		cl.SetFilter(filtercol, filtervals)
	if groupby:
		cl.SetGroupBy(groupby, SPH_GROUPBY_ATTR, groupsort)
	if sortby:
		cl.SetSortMode(SPH_SORT_EXTENDED, sortby)
	if limit:
		cl.SetLimits(0, limit, max(limit, 1000))

	# index = 'lives_main lives_delta'
	index = index
	q = '*{}*'.format(q)
	res = cl.Query ( q, index )

	if not res:
		print('query failed: %s' % cl.GetLastError())
		current_app.logger.error('query failed: %s' % cl.GetLastError())
		sys.exit(1)

	if cl.GetLastWarning():
		print('WARNING: %s\n' % cl.GetLastWarning())
		current_app.logger.error('WARNING: %s\n' % cl.GetLastWarning())

	print('Query \'%s\' retrieved %d of %d matches in %s sec' % (q, res['total'], res['total_found'], res['time']))
	print('Query stats:')

	if 'words' in res:
		for info in res['words']:
			print('\t\'%s\' found %d times in %d documents' % (info['word'], info['hits'], info['docs']))

	if 'matches' in res:
		attrs_list = []
		n = 1
		print('\nMatches:')
		obj_id_list = []
		for match in res['matches']:
			attrsdump = ''
			# for attr in res['attrs']:
			# 	attrname = attr[0]
			# 	attrtype = attr[1]
			# 	value = match['attrs'][attrname]
			# 	print('value===', value)
			# 	if attrtype==SPH_ATTR_TIMESTAMP:
			# 		print('7777')
			# 		value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value) )
			# 		print('===value', value)
			# 		# value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value)).decode("utf-8")
			# 	# attrsdump = '%s, %s=%s' % (attrsdump, attrname, value)
			# 	if attrname == b'id':
			# 		attrsdump = '%s=%s' % (attrname, value)
			# 		print('attrsdump===', attrsdump)
			# 		content_int = int(attrsdump[14:])
			# 		if content_int:
			# 			attrs_list.append(content_int)
			obj_id_list.append(match.get('id'))
		n += 1
		return obj_id_list





#
# $Id$
#




# from sphinxapi3 import *
# import sys, time
#
# if not sys.argv[1:]:
# 	print("Usage: python test.py [OPTIONS] query words\n")
# 	print("Options are:")
# 	print("-h, --host <HOST>\tconnect to searchd at host HOST")
# 	print("-p, --port\t\tconnect to searchd at port PORT")
# 	print("-i, --index <IDX>\tsearch through index(es) specified by IDX")
# 	print("-s, --sortby <EXPR>\tsort matches by 'EXPR'")
# 	print("-a, --any\t\tuse 'match any word' matching mode")
# 	print("-b, --boolean\t\tuse 'boolean query' matching mode")
# 	print("-e, --extended\t\tuse 'extended query' matching mode")
# 	print("-f, --filter <ATTR>\tfilter by attribute 'ATTR' (default is 'group_id')")
# 	print("-v, --value <VAL>\tadd VAL to allowed 'group_id' values list")
# 	print("-g, --groupby <EXPR>\tgroup matches by 'EXPR'")
# 	print("-gs,--groupsort <EXPR>\tsort groups by 'EXPR'")
# 	print("-l, --limit <COUNT>\tretrieve COUNT matches (default is 20)")
# 	sys.exit(0)
#
# q = 'test'
# mode = SPH_MATCH_ALL
# host = '192.168.2.88'
# port = 9312
# index = '*'
# filtercol = 'group_id'
# filtervals = []
# sortby = ''
# groupby = ''
# groupsort = '@group desc'
# limit = 0
#
# i = 1
# while (i<len(sys.argv)):
# 	arg = sys.argv[i]
# 	if arg=='-h' or arg=='--host':
# 		i += 1
# 		host = sys.argv[i]
# 	elif arg=='-p' or arg=='--port':
# 		i += 1
# 		port = int(sys.argv[i])
# 	elif arg=='-i':
# 		i += 1
# 		index = sys.argv[i]
# 	elif arg=='-s':
# 		i += 1
# 		sortby = sys.argv[i]
# 	elif arg=='-a' or arg=='--any':
# 		mode = SPH_MATCH_ANY
# 	elif arg=='-b' or arg=='--boolean':
# 		mode = SPH_MATCH_BOOLEAN
# 	elif arg=='-e' or arg=='--extended':
# 		mode = SPH_MATCH_EXTENDED
# 	elif arg=='-f' or arg=='--filter':
# 		i += 1
# 		filtercol = sys.argv[i]
# 	elif arg=='-v' or arg=='--value':
# 		i += 1
# 		filtervals.append ( int(sys.argv[i]) )
# 	elif arg=='-g' or arg=='--groupby':
# 		i += 1
# 		groupby = sys.argv[i]
# 	elif arg=='-gs' or arg=='--groupsort':
# 		i += 1
# 		groupsort = sys.argv[i]
# 	elif arg=='-l' or arg=='--limit':
# 		i += 1
# 		limit = int(sys.argv[i])
# 	else:
# 		q = '%s%s' % ( q, arg )
# 		q = '@title 比特币'
# 		# q = 'btc'
# 	i += 1
#
# # do query
# cl = SphinxClient()
# cl.SetServer ( host, port )
# # cl.SetMatchMode ( mode )
# cl.SetMatchMode ( SPH_MATCH_EXTENDED )
#
# if filtervals:
# 	cl.SetFilter ( filtercol, filtervals )
# if groupby:
# 	cl.SetGroupBy ( groupby, SPH_GROUPBY_ATTR, groupsort )
# if sortby:
# 	cl.SetSortMode ( SPH_SORT_EXTENDED, sortby )
# if limit:
# 	cl.SetLimits ( 0, limit, max(limit,1000) )
#
# index = 'news_main news_delta'
# res = cl.Query ( q, index )
#
# if not res:
# 	print('query failed: %s' % cl.GetLastError())
# 	sys.exit(1)
#
# if cl.GetLastWarning():
# 	print('WARNING: %s\n' % cl.GetLastWarning())
#
# print('Query \'%s\' retrieved %d of %d matches in %s sec' % (q, res['total'], res['total_found'], res['time']))
# print('Query stats:')
#
# if 'words' in res:
# 	for info in res['words']:
# 		print('\t\'%s\' found %d times in %d documents' % (info['word'], info['hits'], info['docs']))
#
# if 'matches' in res:
# 	n = 1
# 	print('\nMatches:')
# 	for match in res['matches']:
# 		attrsdump = ''
# 		for attr in res['attrs']:
# 			attrname = attr[0]
# 			attrtype = attr[1]
# 			value = match['attrs'][attrname]
# 			if attrtype==SPH_ATTR_TIMESTAMP:
# 				value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value) )
# 			attrsdump = '%s, %s=%s' % ( attrsdump, attrname, value )
#
# 		print('%d. doc_id=%s, weight=%d%s' % (n, match['id'], match['weight'], attrsdump))
# 		n += 1
