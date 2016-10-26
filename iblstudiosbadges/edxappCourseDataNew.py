

import sys, os
import collections

from pymongo import Connection

# FYI: mongodb hierarchy
# course -> id.category : course
    # section -> id.category : chapter
        # subsection -> _id.category : sequential
            # problem -> _id.category : vertical


def getMongoCourseObjectID(conn, course_slug):
    objid = ''
    if course_slug != '' and course_slug != None:
        rquery = conn.find({"run":""+course_slug["run"]+"","course":""+course_slug["course"]+"","org":""+course_slug["org"]+""}, {"versions.published-branch":1, "_id":0 })
        for doc in rquery:
            objid = doc["versions"]["published-branch"]
    return objid

def getCourseSlug(course_id):
    """
    schemma wiki_slug: org.course.run
        ie. course-v1:IBL+BG01+2016_T3
        res IBL.BG01.2016_T3
    """
    if course_id != '' and course_id != 'None':
        splitcourse = course_id.split(':')
        course_slug = splitcourse[1]
        course = course_slug.split('+')
        corg = course[0]
        ccourse = course[1]
        crun = course[2]
        if corg != '' and ccourse != '' and crun != '':
            dic_course = {"org":corg,"run":crun,"course":ccourse}
            return dic_course
        else:
            return ''

def getCompleteCourseStructure(conn, conn2, cobjid, xblock_category):
    from bson.objectid import ObjectId

    dic_course = {}
    list_chapters = []
    list_sequentials = []
    list_verticals = []
    list_problems = []
    list_badges = []
    
    if cobjid != '':
        res_query = conn.find({'_id': ObjectId(cobjid) })
        for dic in res_query:
            # print dic
            for k in dic['blocks']:
                objid = k["definition"]
                block_type = k["block_type"]
                block_id = k["block_id"]
                # childrens
                childrens = []
                if 'children' in k["fields"]:
                    childrens = k["fields"]["children"]
                # weight
                weight = 0
                # append dicts
                if block_type == "problem":
                    weight = 1
                    if 'weight' in k["fields"]:
                        weight = k["fields"]["weight"]
                    list_problems.append({'definition':objid, 'block_type':block_type, "block_id":block_id, "childrens":childrens, 'weight': weight})
                if block_type == "chapter":
                    list_chapters.append({'definition':objid, 'block_type':block_type, "block_id":block_id, "childrens":childrens, 'weight': weight})
                if block_type == "sequential":
                    list_sequentials.append({'definition':objid, 'block_type':block_type, "block_id":block_id, "childrens":childrens, 'weight': weight})
                if block_type == "vertical":
                    list_verticals.append({'definition':objid, 'block_type':block_type, "block_id":block_id, "childrens":childrens, 'weight': weight})
                if block_type == xblock_category:
                    badge_data = getBadgeScore(conn2, objid, xblock_category)
                    badge_id = badge_data["bg_id"]
                    badge_score = badge_data["req_score"]
                    list_badges.append({'definition':objid, 'block_type':block_type, "block_id":block_id, "childrens":childrens, 'weight': weight, 'badge_id': badge_id, 'badge_score':badge_score})

    dic_course = { "chapters": list_chapters,
                   "sequentials": list_sequentials ,
                   "verticals": list_verticals,
                   "problems" : list_problems,
                   "badges" : list_badges }
    
    # return dic_badges
    return dic_course


def getProblemsFromGivenBadgeID(dic_course, badgeid):

    badge_req_score = "0"
    badge_block_id = ""
    for k, v in dic_course.items():
        if k == "badges":
            for key in v:
                if key["badge_id"] == badgeid:
                    badge_block_id = key["block_id"]
                    badge_req_score = key["badge_score"]

    if badge_block_id != '':
        for k, v in dic_course.items():
            if k == "verticals":
                for key in v:
                    for e in key["childrens"]:
                        if badge_block_id in e:
                            badge_vertical_block_id = key["block_id"]
    
        for k, v in dic_course.items():
            if k == "sequentials":
                for key in v:
                    for e in key["childrens"]:
                        if badge_vertical_block_id in e:
                            badge_sequential_block_id = key["block_id"]
    
        for k, v in dic_course.items():
            if k == "chapters":
                for key in v:
                    for e in key["childrens"]:
                        if badge_sequential_block_id in e:
                            badge_chapter_block_id = key["block_id"]
                            sequentials_childrens = key["childrens"]

    # recursive filters : construct dic_problems 
    dic_problems = {}
    list_selected_problems = []
    total_problems_score = 0
    if sequentials_childrens:
        for k, v in sequentials_childrens:
            for e in dic_course["sequentials"]:
                if v == e["block_id"] and v == badge_sequential_block_id:
                #get all course problems: only for course-v1 versions
                #if v == e["block_id"]:
                    dic_childrens_seq = e["childrens"]
                    for seq, vertical in dic_childrens_seq:
                        for f in dic_course["verticals"]:
                           if vertical == f["block_id"]:
                               dic_childrens_problems = f["childrens"]
                               for childp, problem_id in dic_childrens_problems:
                                   if childp == "problem":
                                       for p in dic_course["problems"]:
                                           if p["block_id"] == problem_id:
                                               if p["weight"] > 0:
                                                   # total_problems_score += p["weight"]
                                                   total_problems_score += 1
                                               list_selected_problems.append({"problem_id":problem_id, 'problem_score': p["weight"]})

    dic_problems = { "badge_req_score":badge_req_score, "problems": list_selected_problems, "total_problems_score":total_problems_score }
    return dic_problems


def getBadgeScore(conn, cobjid, xblock_category, badgeid='0'):
    from bson.objectid import ObjectId
    req_score = "-1"
    bg_id = "0"
    if badgeid != '' and badgeid != '0':
        res_query = conn.find({'_id': ObjectId(cobjid), "block_type":xblock_category, "fields.bg_id":badgeid }, { "fields.required_score":1 , "fields.bg_id":1  });
    else:
        res_query = conn.find({'_id': ObjectId(cobjid), "block_type":xblock_category}, { "fields.required_score":1 , "fields.bg_id":1 });        
    for dic in res_query:
        for k in dic['fields']:
            if k == "required_score":
                req_score = dic["fields"]["required_score"]
            if k == "bg_id":
                bg_id = dic["fields"]["bg_id"]
    data = {"bg_id":bg_id, "req_score": req_score }
    return data
