import sys, os
import collections

from pymongo import Connection


# FYI: mongodb hierarchy
# course -> id.category : course
    # section -> id.category : chapter
        # subsection -> _id.category : sequential
            # problem -> _id.category : vertical

""" Get data recursively """
def getRecursiveData(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(getRecursiveData, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(getRecursiveData, data))
    else:
        return data

""" Get Chapters : sections """
def getCourseChapters(dict_course,xblock_category):
    res_list = []
    if len(dict_course)>0:
        for i, v in enumerate(dict_course):
            _id = v.get('_id')
            definition = v.get('definition')
            metadata = v.get('metadata')
            if v.get('_id')['category'] == 'course':
                chapters = definition['children']
                if len(chapters)>0:
                    for k in chapters:
                        sequentials = getCourseSequentials(dict_course,k.split('/')[::-1][0],xblock_category)
                        res_list.append( {'category': 'chapter', 'module_id' : k, 'name' : k.split('/')[::-1][0], 'chapters': sequentials } )
    return res_list

""" Get Sequentials : subsections """
def getCourseSequentials(dict_course,cname,xblock_category):
    res_list = []
    if len(dict_course)>0:
        for i, v in enumerate(dict_course):
            if v.get('_id')['name']==cname and v.get('_id')['category']=='chapter':
                children = v.get('definition')['children']
                if len(children)>0:
                    for k in children:
                        verticals = getCourseVerticals(dict_course,k.split('/')[::-1][0],xblock_category)
                        res_list.append( {'category': 'sequential', 'module_id' : k, 'name' : k.split('/')[::-1][0], 'verticals': verticals } )
    return res_list

""" Get Verticals : for group problems in subsection """
def getCourseVerticals(dict_course,cname,xblock_category):
    res_list = []
    if len(dict_course)>0:
        for i, v in enumerate(dict_course):
            if v.get('_id')['name']==cname and v.get('_id')['category']=='sequential':
                children = v.get('definition')['children']
                items  = []
                if len(children)>0:
                    for k in children:
                        items = getCourseItems(dict_course,k.split('/')[::-1][0],xblock_category)
                        total_score = getCourseVerticalsScore(dict_course,cname,xblock_category)
                        res_list.append( {'category': 'vertical', 'module_id' : k, 'name' : k.split('/')[::-1][0], 'items': items , 'total_score': total_score} )
    return res_list

"""
Get Items : last level
filter: problems and category_badges
"""
def getCourseItems(dict_course,cname,xblock_category):
    res_list = []
    badge_id = 0
    item_score = 0
    total_score = 0
    if len(dict_course)>0:
        for i, v in enumerate(dict_course):
            if v.get('_id')['name']==cname and v.get('_id')['category']=='vertical':
                children = v.get('definition')['children']
                if len(children)>0:
                    for k in children:
                        item_name = k.split('/')[::-1][0]
                        for item,val in enumerate(dict_course):
                            if val.get('_id')['name']==item_name and (val.get('_id')['category']=='problem' or val.get('_id')['category']==''+xblock_category+''):
                                category = val.get('_id')['category']
                                revision = val.get('_id')['revision']
                                metadata = val.get('metadata')
                                definition = val.get('definition')
                                if category ==''+xblock_category+'' and revision!='draft':
                                    if 'bg_id' in definition['data']:
                                        badge_id = val.get('definition')['data']['bg_id']
                                    else:
                                        badge_id = 0
                                    res_list.append( {'category': category, 'module_id' : k, 'name' : item_name,'badge_id': badge_id, 'item_score': item_score } )
                                else:
                                    if category =='problem' and revision!='draft':
                                        item_score = 0 #init
                                        if 'weight' in metadata:
                                            item_score= metadata['weight']
                                        if item_score==0: item_score=1
                                        res_list.append( {'category': category, 'module_id' : k, 'name' : item_name,'badge_id': badge_id, 'item_score': item_score } )
    return res_list

""" Get Verticals Score : total subsections """
def getCourseVerticalsScore(dict_course,cname,xblock_category):
    res_list = []
    total_score = 0
    if len(dict_course)>0:
        for i, v in enumerate(dict_course):
            if v.get('_id')['name']==cname and v.get('_id')['category']=='sequential':
                children = v.get('definition')['children']
                items  = []
                if len(children)>0:
                    for k in children:
                        items            = getCourseItems(dict_course,k.split('/')[::-1][0],xblock_category)
                        for item in items:
                            item_score = item['item_score']
			    try:
				    my_value = int(item_score)
			    except TypeError:
				    my_value = 0  # 

                            total_score += my_value
    return total_score

"""
Get all data from mongo database
for the given course as a dictionary
"""
def getDictCompleteCourseData(conn,course_id,xblock_category):
    course = setParseCourseId(course_id)
    dict_course = []
    if course!='':
        corg = course[0]
        ccourse = course[1]
        cname = course[2]
        res_query = conn.find({'_id.org': ''+corg+'', '_id.course': ''+ccourse+'', '_id.category': { "$in": [ 'course','chapter', 'sequential', 'vertical','problem', ''+xblock_category+'' ] } }, {'definition.children':1, 'definition.data.bg_id':1, 'metadata.weight':1})
        if res_query:
            for item in res_query:
                dict_course.append( getRecursiveData(item) )
    return dict_course

"""
Get a complete list of problems
for the given course_id
"""
def getCompleteListProblems(conn,course_id,xblock_category):
    result_dict = []
    dict_course = getDictCompleteCourseData(conn,course_id,xblock_category)
    if len(dict_course)>0:
        res_complete = getCourseChapters(dict_course,xblock_category)
        for k1 in res_complete:
            chapters = k1['chapters']
            for k2 in chapters:
                chapter_module_id = k2['module_id']
                verticals = k2['verticals']
                for k3 in verticals:
                    vertical_module_id = k3['module_id']
                    vertical_total_score = k3['total_score']
                    items = k3['items']
                    for k4 in items:
                        data_list = {'chapter_module_id':chapter_module_id, 'vertical_module_id':vertical_module_id,
                                    'item_module_id':k4['module_id'],'item_category':k4['category'],
                                    'item_badge_id': k4['badge_id'], 'item_score':k4['item_score'], 'chapter_max_score':vertical_total_score
                                    }
                        result_dict.append(data_list)
    return result_dict

""" Parse course_id name """
def setParseCourseId(course_id):
    if course_id !='' and course_id !='None':
        course  = course_id.split('/')
        corg= course[0]
        ccourse = course[1]
        cname = course[2]
        if corg!='' and ccourse!='' and cname!='':
            return course
        else:
            return ''

""" Get a complete list of problems for a given badge id """
def getListProblemsFromBadgeId(conn,badge_id,course_id,xblock_category):
    chapter_module_id =''
    problems_list     =[]
    if course_id!='' and course_id!='None' and badge_id!='' and badge_id!='None':
        dict_course = getCompleteListProblems(conn,course_id,xblock_category)
        if len(dict_course)>0:
            for k in dict_course:
                if k['item_badge_id'] == badge_id:
                    chapter_module_id = k['chapter_module_id']
        if chapter_module_id !='':
            for p in dict_course:
                if p['chapter_module_id'] == chapter_module_id:
                    #print ('%s : %s') % (p['item_module_id'],p['item_score'])
                    problems_list.append({ 'problem_id':p['item_module_id'], 'problem_score':p['item_score'] } )
    return problems_list

""" Get the score from a given course and badge """
def getScoreFromBadgeId(conn,badge_id,course_id,xblock_category):
    score = '0'
    problems_list=[]
    if course_id!='' and course_id!='None' and badge_id!='' and badge_id!='None':
        dict_course = getCompleteListProblems(conn,course_id,xblock_category)
        if len(dict_course)>0:
            for k in dict_course:
                if k['item_badge_id'] == badge_id:
                    score = k['chapter_max_score']
    return score
