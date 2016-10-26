



import sys, os
import collections
import edxappCourseData
import edxappCourseDataNew

from pymongo import Connection

def getMongoCourseVersion(course_id):
    if course_id != '' and course_id != 'None':
        if "course-v1:" in course_id.lower():
            return 'new'
    return 'old'

def resultBadgesScores(self):
    """
    Get student data from the DBs
    """
    # the appmysqldb module will only be used here
    import appmysqldb
    # init default data
    user_id = "None"
    course_id = "None"
    user_name = "None"
    user_email = "None"
    user_score = "0"
    # user and course
    db = appmysqldb.mysql('localhost', 3306, self.mysql_database, self.mysql_user, '')
    q = "SELECT id, user_id, course_id FROM student_anonymoususerid WHERE anonymous_user_id='" + self.n_user_id + "'"
    db.query(q)
    res = db.fetchall()
    for row in res:
        user_id = row[1]
        course_id = row[2]
    # username
    q = "SELECT name FROM auth_userprofile WHERE user_id='%s' " % (user_id)
    db.query(q)
    res = db.fetchall()
    for row in res:
        user_name = row[0]
    # email
    q = "SELECT email FROM auth_user WHERE id='%s' " % (user_id)
    db.query(q)
    res = db.fetchall()
    for row in res:
        user_email = row[0]
    
    versionXblockBadges = getMongoCourseVersion(course_id)
    # print "XBLOCK BADGES VERSION %s" % (versionXblockBadges)

    # edx old versions
    if versionXblockBadges == 'old':
        # course data from mongodb
        from pymongo import Connection
        xmoduledb = self.xblock_mongodb_xmoduledb
        connection = Connection()
        db_mongo = connection[xmoduledb]
        mongo_modulestore = db_mongo[self.xblock_mongodb_modulestore]
        badge_list_problems = edxappCourseData.getListProblemsFromBadgeId(mongo_modulestore, self.bg_id, course_id, self.xblock_name_field)
        badge_problems_score = edxappCourseData.getScoreFromBadgeId(mongo_modulestore, self.bg_id, course_id, self.xblock_name_field)
        # calculate badge_score
        user_score = 0
        partial_user_score = []
        badge_partial_user_score = 0
        badge_percent_user_score = 0
        # calculate user partials
        if badge_problems_score > 0:
            if len(badge_list_problems) > 0:
                for problem in badge_list_problems:
                    if 'problem_score' in problem:
                        problem_score = problem['problem_score']
                        problem_id = problem['problem_id']
                        # partial values
                        if int(problem_score) > 0:
                            q = "SELECT ((%s/max_grade)*grade) FROM courseware_studentmodule WHERE course_id='%s' AND student_id='%s' AND module_id='%s'" % (problem_score, course_id, user_id, problem_id)
                            db.query(q)
                            res = db.fetchall()
                            for row in res:
                                if row[0] > 0:
                                    partial_user_score.append(float(row[0]))
                        badge_partial_user_score = sum(partial_user_score)
        # calculate total percent
        if round(badge_partial_user_score, 2) > 0 and int(badge_problems_score) > 0:
            badge_percent_user_score = (badge_partial_user_score * 100.0) / badge_problems_score
            badge_percent_user_score = round(badge_percent_user_score, 2)
        if int(badge_percent_user_score) > 0:
            user_score = badge_percent_user_score
    
    # edx new versions
    else:
        badge_list_problems = {}
        user_score = 0
        partial_user_score = []
        badge_partial_user_score = 0
        badge_percent_user_score = 0        
        badge_problems_score = 0
        
        # course data from mongodb
        from pymongo import Connection
        xmoduledb = self.xblock_mongodb_xmoduledb
        connection = Connection()
        db_mongo = connection[xmoduledb]
        mongo_modulestore_structures = db_mongo[self.xblock_mongodb_modulestore_structures]
        mongo_modulestore_activevers = db_mongo[self.xblock_mongodb_modulestore_activevers]
        mongo_modulestore_definitions = db_mongo[self.xblock_mongodb_modulestore_definitions]
        
        course_slug = edxappCourseDataNew.getCourseSlug(course_id)
        if course_slug != '':
            course_objid = edxappCourseDataNew.getMongoCourseObjectID(mongo_modulestore_activevers, course_slug)
            dic_course = edxappCourseDataNew.getCompleteCourseStructure(mongo_modulestore_structures, mongo_modulestore_definitions, course_objid, self.xblock_name_field)
            dic_problems = edxappCourseDataNew.getProblemsFromGivenBadgeID(dic_course, self.bg_id)       
        
        if dic_problems:
            badge_list_problems = dic_problems["problems"]
            total_problems_score = dic_problems["total_problems_score"]
            # badge_problems_score = dic_problems["badge_req_score"]
            badge_problems_score = total_problems_score

        # calculate badge_score
        if badge_problems_score > 0:
            if len(badge_list_problems) > 0:
                for problem in badge_list_problems:
                    if 'problem_score' in problem:
                        problem_score = problem['problem_score']
                        problem_id = problem['problem_id']
                        # partial values
                        if int(problem_score) > 0:
                            # q1 = "SELECT ((%s/max_grade)*grade) FROM courseware_studentmodule " % (problem_score)
                            q1 = "SELECT (grade/max_grade) FROM courseware_studentmodule "
                            q2 = "WHERE course_id='%s' AND student_id='%s' AND module_type='problem' " % (course_id, user_id)
                            q3 = "AND grade IS NOT NULL "
                            q4 = "AND module_id LIKE '%@" + problem_id + "'"
                            q = "%s%s%s%s" % (q1, q2, q3, q4)
                            db.query(q)
                            res = db.fetchall()
                            for row in res:
                                if row[0] > 0:
                                    partial_user_score.append(float(row[0]))
                                    badge_partial_user_score = sum(partial_user_score)
            # calculate total percent
            if round(badge_partial_user_score, 2) > 0 and int(badge_problems_score) > 0:
                badge_percent_user_score = (badge_partial_user_score * 100.0) / int(badge_problems_score)
                badge_percent_user_score = round(badge_percent_user_score, 2)
            if int(badge_percent_user_score) > 0:
                user_score = badge_percent_user_score        

    # show results
    results = [user_id, course_id, user_name, user_email, user_score, badge_list_problems,
               badge_problems_score, badge_partial_user_score, badge_percent_user_score, badge_problems_score]
    return results
