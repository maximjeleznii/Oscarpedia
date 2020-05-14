import unittest
from app.routes import query_all, query_args, query_search, add_result

#Test all movie return
def test_query_all():
    testlist = '[<Movie 1>, <Movie 2>, <Movie 3>, <Movie 4>, <Movie 5>, <Movie 6>, <Movie 7>, <Movie 8>, <Movie 9>, <Movie 10>]'
    assert str(query_all()) == testlist

#Test query results for querystring arguments
def test_query_args():
    arg1 = {'foo' : '%$%'}
    arg2 = {'name' : 'gladiator'}
    arg3 = {'year' : '2000'}
    arg4 = {'oscars' : 'picture'}
    assert str(query_args(arg1)) == '[]'
    assert str(query_args(arg2)) == '[<Movie 1>]'
    assert str(query_args(arg3)) == '[<Movie 1>, <Movie 2>, <Movie 3>, <Movie 4>, <Movie 5>, <Movie 6>, <Movie 7>, <Movie 8>, <Movie 9>, <Movie 10>]'
    assert str(query_args(arg4)) == '[<Movie 1>]'

#Test query results for a search for all columns
def test_query_search():
    arg1 = '%$%'
    arg2 = 'gladiator'
    arg3 = '2000'
    arg4 = 'picture'
    arg5 = ''
    arg6 = 'pollock'
    assert str(query_search(arg1)) == '[]'
    assert str(query_search(arg2)) == '[<Movie 1>]'
    assert str(query_search(arg3)) == '[<Movie 1>, <Movie 2>, <Movie 3>, <Movie 4>, <Movie 5>, <Movie 6>, <Movie 7>, <Movie 8>, <Movie 9>, <Movie 10>]'
    assert str(query_search(arg4)) == '[<Movie 1>]'
    assert str(query_search(arg5)) == '[<Movie 1>, <Movie 2>, <Movie 3>, <Movie 4>, <Movie 5>, <Movie 6>, <Movie 7>, <Movie 8>, <Movie 9>, <Movie 10>]'
    assert str(query_search(arg6)) == '[<Movie 4>]'

#Test adding of lists of movies
def test_add_result():
    list1 = query_search('gladiator')
    list2 = query_search('pollock')
    assert str(add_result(list1, list2)) == '[<Movie 1>, <Movie 4>]'