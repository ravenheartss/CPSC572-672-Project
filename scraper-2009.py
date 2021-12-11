# python3 
# CPSC 672 Project
# Scrapes the 2009 UofC CPSC course calendar

# This entire script is a mess but it works. We didn't have the time to clean it up.
# It takes a maximum of 30s on my machine (i9 8-core 2.5Ghz). 
# This script can be used differently on what function we use to get edges
# I shoudld've added command line args but didn't in the end. 


# Import statements
import requests
import string
import json
import re
from bs4 import BeautifulSoup
import copy
import itertools as it
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import powerlaw

# Settings for matplotlib
mpl.rc('xtick', labelsize=14, color="#222222") 
mpl.rc('ytick', labelsize=14, color="#222222") 
mpl.rc('font', **{'family':'sans-serif','sans-serif':['Arial']})
mpl.rc('font', size=16)
mpl.rc('xtick.major', size=6, width=1)
mpl.rc('xtick.minor', size=3, width=1)
mpl.rc('ytick.major', size=6, width=1)
mpl.rc('ytick.minor', size=3, width=1)
mpl.rc('axes', linewidth=1, edgecolor="#222222", labelcolor="#222222")
mpl.rc('text', usetex=False, color="#222222")

# Global vars
coursesDict = []
courses_dict = {}
prereqList = []
G = None

# These lines of code are an abomination.
# It's used to remove certain phrases from pre-req and anti-req
pattern1 = re.compile(re.escape('and consent of the department'), re.IGNORECASE)
pattern2 = re.compile(re.escape('with department consent'), re.IGNORECASE)
pattern3 = re.compile(re.escape('consent of the department'), re.IGNORECASE)
pattern4 = re.compile(re.escape('; and 6 units offered by the faculty of science'), re.IGNORECASE)
pattern5 = re.compile(re.escape("Pure Mathematics 30 or Mathematics II (offered by Continuing Education)."), re.IGNORECASE)
pattern6 = re.compile(re.escape("A grade of 70 per cent or higher in Pure Mathematics 30. (Alternatives are presented in the paragraph titled Mathematics Diagnostic Test in the Program section of this Calendar.)"), re.IGNORECASE)
pattern7 = re.compile(re.escape("A grade of 70 per cent or higher in Pure Mathematics 30."), re.IGNORECASE)
pattern8 = re.compile(re.escape("A grade of 70 per cent or higher in Pure Mathematics 30 and a grade of 50 per cent or higher in Mathematics 31. (Alternatives to Pure Mathematics 30 are presented in the paragraph titled Mathematics Diagnostic Test in the Program section of this Calendar.)"), re.IGNORECASE)
pattern9 = re.compile(re.escape('A grade of 80 per cent or higher in Pure Mathematics 30 and a grade of 50 per cent or higher in Mathematics 31. (Alternatives to Pure Mathematics 30 are presented in the paragraph titled Mathematics Diagnostic Test in the Program section of this Calendar.)'), re.IGNORECASE)
pattern9 = re.compile(re.escape('a grade of B+ or better in'), re.IGNORECASE)
pattern10 = re.compile(re.escape('or equivalent'), re.IGNORECASE)
pattern11 = re.compile(re.escape('a grade of B+ or better in'), re.IGNORECASE)
pattern12 = re.compile(re.escape('Prerequisites for Computer and Software Engineering students: Computer Science 457 and one of Computer Engineering 415, 417 or 511. Prerequisites for Computer Science students:'), re.IGNORECASE)
pattern13 = re.compile(re.escape('A grade of 70% or higher in Pure Mathematics 30 and credit in Mathematics 31; or admission to the Faculty of Engineering including credit in Pure Mathematics 30 and Mathematics 31.'), re.IGNORECASE)
pattern14 = re.compile(re.escape('or consent of Applied Mathematics Division'), re.IGNORECASE)
pattern15 = re.compile(re.escape('or consent of the Division'), re.IGNORECASE)
pattern16 = re.compile(re.escape('Pure Mathematics 30 or Mathematics II (offered by Continuing Education).'), re.IGNORECASE)
pattern17 = re.compile(re.escape('or any Statistics course, or consent of the Division.'), re.IGNORECASE)
pattern18 = re.compile(re.escape('(Pure Mathematics 419)'), re.IGNORECASE)
pattern18 = re.compile(re.escape('Not open to students with'), re.IGNORECASE)
pattern19 = re.compile(re.escape(', (For students registered in Software Engineering, Schulich School of Engineering) Software Engineering 301'), re.IGNORECASE)
pattern20 = re.compile(re.escape('(For students registered in Computer Science)'), re.IGNORECASE)
pattern21 = re.compile(re.escape('Consent of either the Department of Electrical and Computer Engineering or the Department of Computer Science.'), re.IGNORECASE)

# Dictionary of all the relevant dept code and it's name
codes = {
        "computer science": 'CPSC',
        "pure mathematics": 'PMAT',
        "applied mathematics": 'AMAT',
        "mathematics": 'MATH',
        "statistics": 'STAT',
        "electrical engineering": 'ENEL',
        "chemical engineering": 'ENCH',
        "digital engineering": 'ENDG',
        "software engineering for engineers": 'ENSF',
        "data science": 'DATA',
        "software engineering": 'SENG',
        "business technology management": 'BTMA',
        "computer engineering": 'ENCM',
        "philosophy": "PHIL",
        "engineering": 'ENGG',
        'management information systems': 'MGIS',
        'business and environment': 'BSEN',
    }

# Dictionary of all dept course URL
urls = {
        'MATH': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/computer-science.html',
        'STAT': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/computer-science.html',
        'ENEL': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/electrical-engineering.html',
        'ENCH': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/chemical-science.html',
        'ENSF': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/software-engineering-for-engineers.html',
        'DATA': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/data-science.html',
        'SENG': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/software-engineering.html',
        'MGIS': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/management-information-systems.html',
        'ENCM': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/computer-engineering.html',
        'PHIL': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/philosophy.html',
        'ENGG': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/engineering.html',
        'PMAT': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/pure-mathematics.html',
        'AMAT': 'https://www.ucalgary.ca/pubs/calendar/archives/2009/applied-mathematics.html'
    }


# Scrapes the CPSC course calendar
def getCourseList():
    global coursesDict
    URL = "https://www.ucalgary.ca/pubs/calendar/archives/2009/computer-science.html"

    page = requests.get(URL)
    bsoup = BeautifulSoup(page.content, 'html.parser')

    # Get course code and name
    courses = bsoup.find_all(class_='course-code')
    # Add course to coursesDict
    # Each course has 3 tags in courses (dpt name, code, name)
    for i in range(0, len(courses), 3):
        course = {}
        # This is the unique identifier for a course and is used in CSS/HTML classes and ids.
        ID = courses[i].get('id')
        ID = ID[:ID.rfind('_')]
        
        # Get prereq string for the course
        # Remove unncessary information from prereq string
        prereqs = bsoup.find_all(id=ID+"_cnPrerequisites", class_='course-prereq')
        prereqs = prereqs[0].text.strip('\n').lower()
        prereqs = pattern4.sub('', pattern3.sub('', pattern2.sub('', pattern1.sub('', prereqs))))
        prereqs = pattern5.sub('', pattern6.sub('', pattern7.sub('', pattern8.sub('', pattern8.sub('', pattern9.sub('', pattern10.sub('', pattern11.sub('', prereqs))))))))
        prereqs = pattern12.sub('', pattern13.sub('', pattern14.sub('', pattern15.sub('', pattern16.sub('', pattern17.sub('', pattern18.sub('', pattern19.sub('', prereqs))))))))
        prereqs = pattern20.sub('', pattern21.sub('', prereqs))
        prereqs = re.sub('and [0-9]* units offered [ 0-9a-zA-Z_]*\.', '', prereqs)
        # This was found in some pre-req string. Dirty way to fix it but considering the time frame
        # and the fact that this script itself is dirty, don't really care as long it gets the job done 
        # and doesn't take a long time
        prereqs = prereqs.replace('\n\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', '')
        
        # Replace all dept name with code
        for x in codes.keys():
            if x in prereqs.lower():
                prereqs = prereqs.lower().replace(x, codes[x])
                
        # Replace 'and' with && and 'or' with ||
        prereqs = prereqs.replace("and", '&&').replace("or", '||')

        antireq = bsoup.find_all(id=ID+"_cnAntirequisites", class_='course-antireq')
        desc = bsoup.find_all(id=ID+'_cnDescription', class_='course-desc')
        hours = bsoup.find_all(id=ID+'_cnHours', class_='course-hours')
        prereqs = prereqs.replace('any one of', '3 units from ')
        prereqs = prereqs.replace('one of', '3 units from ')

        # Append to course list
        course['prereq'] = prereqs
        course['antireq'] = antireq[0].text.strip('\n')
        course['code'] = 'CPSC'+courses[i+1].text.strip('\n')
        course['name'] = courses[i+2].text.strip('\n')
        course['desc'] = desc[0].text.strip('\n')
        course['units'] = hours[0].text.strip('\n').split(';')[0]
        course['prereq-log'] = bsoup.find_all(id=ID+"_cnPrerequisites", class_='course-prereq')[0].text.strip('\n')
        course['antireq-log'] = antireq[0].text.strip('\n')
        coursesDict.append(course)



# Parses all pre-reqs to list with clauses
# Parses the string to 2D lists such that each list inside is an and statement
# and each element inside the list is an or statement
# So [[A,B], [C,D]] means (A or B) and (C or D)
def parsePreReq():
    global coursesDict
    for course in coursesDict:
        test = course['prereq'].replace(';', '')
        reqs = []
        
        if len(test) > 0:
            test = test.replace('.', '')
            test = test.replace('\n\xa0#\xa0\xa0\xa0\xa0\xa0\xa0\xa0', '')
            temp = test.split('&&')
            # Last dept code mentioned
            last_code = ''
            # Each clause in conjuction
            for clause in temp:
                if 'consent' in clause:
                    continue
                toadd = []#
                if '3 units from ' not in clause:
                    splt_clause = clause.split('||')
                    for term in splt_clause:
                        t = term.strip(' ').split(' ')
                        if t[0].upper() in codes.values():
                            last_code = t[0].upper()
                            # If no code detected but a valid course number, add the previous dept code and current miber
                            try:
                                if t[1].isdigit():
                                    toadd.append(term.strip(' ').upper().replace(' ', ''))
                            except IndexError:
                                pass
                        else:
                            if term.strip(' ').replace(' ', '').isdigit():
                                toadd.append(last_code.replace(' ', '') + term.strip(' ').replace(' ', ''))
                    reqs.append(toadd)
                # All courses are 3 units so can take any one of the courses which is an OR statement
                elif '3 units from ' in clause:
                    newclause = clause.replace('3 units from ', '').replace(',', '||')
                    splt_clause = newclause.split('||')
                    for term in splt_clause:
                        t = term.strip(' ').split(' ')
                        if t[0].upper() in codes.values():
                            last_code = t[0].upper()
                            try:
                                if t[1].isdigit():
                                    toadd.append(term.strip(' ').upper().replace(' ', ''))
                            except IndexError:
                                pass
                        else:
                            if term.strip(' ').replace(' ', '').isdigit():
                                toadd.append(last_code.replace(' ', '') + term.strip(' ').replace(' ', ''))
                    reqs.append(toadd)
            # Assign list as prereq
            course['prereq'] = reqs


# parse antireq string
def parseAntiReq():
    global coursesDict
    for course in coursesDict:
        if course['code'] == 'CPSC304':
            course['antireq'] = []
            continue
        # Remove certain unncessary phrases
        for dept in codes.keys():
            course['antireq'] = course['antireq'].lower().replace('Note', '').replace(':', '')
            course['antireq'] = course['antireq'].lower().replace(dept, codes[dept]).replace('not open for registration to cpsc majors', '')
            course['antireq'] = course['antireq'].replace('.', '').replace('will not be allowed', '').replace('and any of', '').replace('credit for', '').replace(',', '')
        antireqs = []

        # Get only course codes
        for x in course['antireq'].split(' '):
            if x.upper() in codes.values():
                last_code = x.upper()
            elif x.isdigit():
                if len(x) > 3:
                    x = x[:3] + '.' + x[3:]
                if last_code+x not in antireqs and last_code+x != course['code']:
                    antireqs.append(last_code+x)
        course['antireq'] = antireqs


# Get a non-CPSC course data
def getCourseData(code):
    global coursesDict
    course = { 
        'code': code,
        'prereq': '',
        'name': '',
        'desc': '',
        'antireq': '',
        'units': '3 units',
        'prereq-log': '',
        'antireq-log': ''}

    if code[:4] not in urls.keys():
        return course
    page = requests.get(urls[code[:4]])
    bsoup = BeautifulSoup(page.content, 'html.parser')
    
    # Get course code and name
    courses = bsoup.find_all(class_='course-code')
    for i in range(0, len(courses), 3):
        if courses[i+1].text.strip('\n') != code[4:]:
            continue
        ID = courses[i].get('id')
        ID = ID[:ID.rfind('_')]

        # Get prereq
        prereqs = bsoup.find_all(id=ID+"_cnPrerequisites", class_='course-prereq')
        prereqs = prereqs[0].text.strip('\n').lower()

        # Again, an abomination
        # Replace phrases which hinder parsing and are unnecessary 
        prereqs = pattern3.sub('', pattern2.sub('', pattern1.sub('', prereqs)))
        prereqs = pattern4.sub('', pattern3.sub('', pattern2.sub('', pattern1.sub('', prereqs))))
        prereqs = pattern5.sub('', pattern6.sub('', pattern7.sub('', pattern8.sub('', pattern8.sub('', pattern9.sub('', pattern10.sub('', pattern11.sub('', prereqs))))))))
        prereqs = pattern12.sub('', pattern13.sub('', pattern14.sub('', pattern15.sub('', pattern16.sub('', pattern17.sub('', pattern18.sub('', pattern19.sub('', prereqs))))))))
        prereqs = pattern20.sub('', pattern21.sub('', prereqs))
        prereqs = re.sub('and [0-9]* units offered [ 0-9a-zA-Z_]*\.', '', prereqs)
        prereqs = re.sub('a grade of [0-9]* [ 0-9a-zA-Z_]*\.*', '', prereqs)
        prereqs = prereqs.replace('\n\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', '')
        
        # Replace dept name with code
        for x in codes.keys():
            if x in prereqs.lower():
                prereqs = prereqs.lower().replace(x, codes[x])
        
        # Same code as in getCourseList()
        # Any one of is the same as OR so replace to 3 units from.
        prereqs = prereqs.replace("and", '&&').replace("or", '||')
        antireq = bsoup.find_all(id=ID+"_cnAntirequisites", class_='course-antireq')
        desc = bsoup.find_all(id=ID+'_cnDescription', class_='course-desc')
        hours = bsoup.find_all(id=ID+'_cnHours', class_='course-hours')
        prereqs = prereqs.replace('any one of', '3 units from ')
        prereqs = prereqs.replace('one of', '3 units from ')

        # If '-' in pre-req, don't consider it as '-' only occurs in high school MATH 30-1 and such courses
        # which are not required for this network
        if '-' in prereqs:
            course['prereq'] = ''
        else:
            course['prereq'] = prereqs
        
        course['antireq'] = antireq[0].text.strip('\n')
        course['code'] = code[:4]+courses[i+1].text.strip('\n')
        course['name'] = courses[i+2].text.strip('\n')
        course['desc'] = desc[0].text.strip('\n')
        course['units'] = hours[0].text.strip('\n').split(';')[0]
        course['prereq-log'] = bsoup.find_all(id=ID+"_cnPrerequisites", class_='course-prereq')[0].text.strip('\n')
        course['antireq-log'] = antireq[0].text.strip('\n')

        return course
    
    # Reach here if course was not found, so return placeholder with just code.
    return course


# Get all prerequisite's prerequisite and anti-requisite until there are none left
# Add them to the course list
# Uses code from parsePreReq, parseAntiReq
def fillPreReqs():
    global prereqList
    global coursesDict
    while len(prereqList) > 0:
        for course in prereqList:
            if len(course) == 0:
                continue
            data = getCourseData(course)
            test = data['prereq'].replace(';', '')
            reqs = []
            
            if len(test) > 0:
                test = test.replace('.', '')
                temp = test.split('&&')
                last_code = ''
                # Each clause in conjuction
                for clause in temp:
                    if 'consent' in clause:
                        continue
                    toadd = []#
                    if '3 units from ' not in clause:
                        splt_clause = clause.split('||')
                        for term in splt_clause:
                            t = term.strip(' ').split(' ')
                            if t[0].upper() in codes.values():
                                last_code = t[0].upper()
                                try:
                                    if t[1].isdigit():
                                        toadd.append(term.strip(' ').upper().replace(' ', ''))
                                except IndexError:
                                    pass
                        else:
                            if term.strip(' ').replace(' ', '').isdigit():
                                toadd.append(last_code.replace(' ', '') + term.strip(' ').replace(' ', ''))
                        reqs.append(toadd)
                    elif '3 units from ' in clause:
                        newclause = clause.replace('3 units from ', '').replace(',', '||')
                        splt_clause = newclause.split('||')
                        for term in splt_clause:
                            t = term.strip(' ').split(' ')
                            if t[0].upper() in codes.values():
                                last_code = t[0].upper()
                                try:
                                    if t[1].isdigit():
                                        toadd.append(term.strip(' ').upper().replace(' ', ''))
                                except IndexError:
                                    pass
                            else:
                                if term.strip(' ').replace(' ', '').isdigit():
                                    toadd.append(last_code.replace(' ', '') + term.strip(' ').replace(' ', ''))
                        reqs.append(toadd)
                data['prereq'] = reqs

            for dept in codes.keys():
                data['antireq'] = data['antireq'].lower().replace(dept, codes[dept]).replace('not open for registration to cpsc majors', '')
                data['antireq'] = data['antireq'].replace('.', '').replace('will not be allowed', '').replace('and any of', '').replace('credit for', '').replace(',', '')
                data['antireq'] = re.sub('Not open to [ a-zA-Z0-9]*\.*', '', data['antireq'])
            antireqs = []
            last_code = ''
            for x in data['antireq'].split(' '):
                if x.upper() in codes.values():
                    last_code = x.upper()
                elif x.isdigit():
                    if len(x) > 2:
                        if len(x) > 3:
                            x = x[:3] + '.' + x[3:]
                        if last_code+x not in antireqs and last_code+x != data['code'] and last_code != '':
                            antireqs.append(last_code+x)
            data['antireq'] = antireqs

            coursesDict.append(data)

            # Remove course from prereq list as it has been added to the course list so 
            # no need to get the data for the course again
            prereqList.remove(course)

            # Check for new courses not in the course list
            coursekeys = [k['code'] for k in coursesDict]
            for c in data['prereq']:
                for x in c:
                    if len(x) > 0 and x not in coursekeys and x not in prereqList:
                        prereqList.append(x)


# Gets all course codes from courses in the network
# In short: Gets all node id/label
def getnodelist():
    nodel = set()

    coursekeys = [k['code'] for k in coursesDict]
    for course in coursesDict:
        nodel.add(course['code'])
        for clause in course['prereq']:
            for crse in clause:
                if len(crse) == 0:
                    continue
                if crse not in coursekeys:
                    # If course was not found in the calendar
                    # Add a placeholder with it's code
                    tmp = {'code': crse, 'name': '', 'desc': '', 'units': '3 units', 'prereq': [['']], 'antireq': [], 'prereq-log': '', 'antireq-log': ''}
                    coursesDict.append(tmp)
                    coursekeys = [k['code'] for k in coursesDict]

                nodel.add(crse)
                if crse not in prereqList and crse not in coursekeys:
                    prereqList.append(crse)

        for areq in course['antireq']:
            if areq not in nodel:
                if len(areq) == 0:
                    continue
                if areq not in coursekeys:
                    # If course was not found in the calendar
                    # Add a placeholder with it's code
                    tmp = {'code': areq, 'name': '', 'desc': '', 'units': '3 units', 'prereq': [['']], 'antireq': [], 'prereq-log': '', 'antireq-log': ''}
                    coursesDict.append(tmp)
                    coursekeys = [k['code'] for k in coursesDict]
                if len(areq) < 7:
                    print(course)
                nodel.add(areq)

    # print("Number of nodes:", len(nodel))

    return list(nodel)


# Returns all edges including anti-requisites
def getEdges():
    global coursesDict, courses_dict
    for crse in coursesDict:
        courses_dict[crse['code']] = crse
    
    edges = []
    for course in coursesDict:
        # If the pre-req is a string, make it an empty 2d list
        if courses_dict[course['code']]['prereq'] == '':
            courses_dict[course['code']]['prereq'] = [[""]]
        
        # Get all unique combinations from pre-req 2d list
        combins = [list(s) for s in it.product(*courses_dict[course['code']]['prereq'])]
        # Sort them in ascending order according to course code 
        for x in range(len(combins)):          
            if len(combins[x]) > 0:
                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if float(combins[x][j][4:]) <= float(combins[x][k][4:]):
                                combins[x].insert(k, combins[x].pop(j))
    
        # Check if Course A is a pre-req to Course B in the combination B A. 
        # If it is, swap the courses
        # As that is the logical path
        for x in range(len(combins)):          
            if len(combins[x]) > 0:
                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if combins[x][k] in courses_dict.keys():
                                for pr in courses_dict[combins[x][k]]['prereq']:
                                    if combins[x][j] in pr:
                                        combins[x].insert(k, combins[x].pop(j))
    
        # Add edge to list
        for option in combins:
            for i in range(0, len(option)):
                if len(option[i]) == 0:
                    continue
                if i == len(option)-1:
                    edges.append(option[i]+' '+course['code'])
                else:
                    if len(option[i+1]) == 0:
                        continue
                    edges.append(option[i]+' '+option[i+1])

        # Add bi-directional edge to list
        for areq in course['antireq']:
            if len(areq) == 0:
                continue
            toadd1 = course['code']+' '+areq
            toadd2 = areq+' '+course['code']
            if toadd1 not in edges and toadd2 not in edges:
                edges.append(toadd1)
                edges.append(toadd2)

    return edges


# Get edges for the visualizer
# Only difference is it does not contain multiple edges between nodes
# Having multiple edges makes the visualizer cluttered and impossible to read
# Same code as getEdges but no multiple edges
def getVisEdges():
    global coursesDict, courses_dict
    for crse in coursesDict:
        courses_dict[crse['code']] = crse
    
    edges = set()
    for course in coursesDict:
        if courses_dict[course['code']]['prereq'] == '':
            courses_dict[course['code']]['prereq'] = [[""]]
        combins = [list(s) for s in it.product(*courses_dict[course['code']]['prereq'])]
        for x in range(len(combins)):          
            if len(combins[x]) > 0:
                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if float(combins[x][j][4:]) <= float(combins[x][k][4:]):
                                combins[x].insert(k, combins[x].pop(j))

        for x in range(len(combins)):          
            if len(combins[x]) > 0:
                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if combins[x][k] in courses_dict.keys():
                                for pr in courses_dict[combins[x][k]]['prereq']:
                                    if combins[x][j] in pr:
                                        combins[x].insert(k, combins[x].pop(j))
    
        for option in combins:
            for i in range(0, len(option)):
                if len(option[i]) == 0:
                    continue
                if i == len(option)-1:
                    edges.add(option[i]+' '+course['code'])
                else:
                    if len(option[i+1]) == 0:
                        continue
                    edges.add(option[i]+' '+option[i+1])

# Uncomment the for block to include anti-req
        # for areq in course['antireq']:
        #     if len(areq) == 0:
        #         continue
        #     toadd1 = course['code']+' '+areq
        #     toadd2 = areq+' '+course['code']
        #     if toadd1 not in edges and toadd2 not in edges:
        #         edges.add(toadd1)
        #         edges.add(toadd2)
    
    # Export pre-reqs as list
    # In order to parse different 
    logic = {}
    for course in courses_dict.keys():
        logic[course] = courses_dict[course]['prereq']
    
    with open("logic_edges.json", "w+") as outfile:
        json.dump(logic, outfile)
    
    return edges


# Returns edges without anti-requisites
# Used for analysis of communities and paths
# Same code as getEdges
def getSimpleEdges():
    global coursesDict, courses_dict
    for crse in coursesDict:
        courses_dict[crse['code']] = crse
    
    edges = []
    for course in coursesDict:

        if courses_dict[course['code']]['prereq'] == '':
            courses_dict[course['code']]['prereq'] = [[""]]
        combins = [list(s) for s in it.product(*courses_dict[course['code']]['prereq'])]
        for x in range(len(combins)):          
            if len(combins[x]) > 0:
                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if float(combins[x][j][4:]) <= float(combins[x][k][4:]):
                                combins[x].insert(k, combins[x].pop(j))

                for i in range(1, len(combins[x])):
                    for j in range(i, 0, -1):
                        for k in range(j-1, -1, -1):
                            if combins[x][k] in courses_dict.keys():
                                for pr in courses_dict[combins[x][k]]['prereq']:
                                    if combins[x][j] in pr:
                                        combins[x].insert(k, combins[x].pop(j))
    
        for option in combins:
            for i in range(0, len(option)):
                if len(option[i]) == 0:
                    continue
                if i == len(option)-1:
                    edges.append(option[i]+' '+course['code'])
                else:
                    if len(option[i+1]) == 0:
                        continue
                    edges.append(option[i]+' '+option[i+1])

    return edges


# Ouptut node and edge lists
# The node attributes has a bug. 
# We never used it though
def outputGraph(nodes, edges):
    global courses_dict
    with open('nodes-2009.csv', 'w+') as f:
        f.write('Id Label Name Desc Units Prereq Antireq\n')
        for node in nodes:
            f.write(node+' '+node+' "'+courses_dict[node]['name'].replace('\n', '')+'" "'+courses_dict[node]['desc'].replace('\n', '')+'" "'+courses_dict[node]['units']+'" "'+course['prereq-log']+'" "'+course['antireq-log']+'"+\n')

    with open('edges-2009.csv', 'w+') as f:
        f.write('Source;Target\n')
        for edge in edges:
            edno = edge.split(' ')
            f.write(edno[0]+';'+edno[1]+'\n')


# Create NetworkX from nodes and edges
def createGraph(nodes, edges):
    global courses_dict, G
    G = None
    G = nx.MultiDiGraph()
    for node in nodes:
        G.add_node(node, name=courses_dict[node]['name'], desc=courses_dict[node]['desc'], units=courses_dict[node]['units'], prereq=courses_dict[node]['prereq-log'], antireq=courses_dict[node]['antireq-log'])
    for edge in edges:
        edno = edge.split(' ')
        G.add_edge(edno[0], edno[1])


# Main function 
if __name__ == '__main__':
    getCourseList()    
    parsePreReq()
    parseAntiReq()

    # Add all pre-req courses to be added and parsed to prereqlist
    coursekeys = [k['code'] for k in coursesDict]
    for course in coursesDict:
        for clause in course['prereq']:
            for crse in clause:
                if len(crse) == 0:
                    continue
                if crse not in prereqList and crse not in coursekeys:
                    prereqList.append(crse)
    

    # Get all pre-req ingo and add to course dictionary
    fillPreReqs()
    nlist = getnodelist()

    # Change to getEdges to get all edges or getVisEdges to get all edges for visualizer
    elist = getSimpleEdges()


    # outputGraph(nlist, elist)
    createGraph(nlist, elist)

    N = len(G)
    L = G.size()
    degrees = [G.degree(node) for node in G]
    kmin = min(degrees)
    kmax = max(degrees)
  

    print("Number of nodes (nx): ", N)
    print("Number of edges (nx): ", L)
    print()
    print("Average degree: ", L/N)
    print()
    print("Minimum degree: ", kmin)
    print("Maximum degree: ", kmax)

    # Uncomment to export to gephi
    # nx.write_gexf(G, './gephiviz-2009-prereq.gexf')

    # Get degree distribution with best fit
    nodes = G.nodes()
    degree = dict(G.degree())
    degseq=[degree.get(k,0) for k in nodes if degree.get(k,0) > 0]
    data = np.array(degseq)
    fit = powerlaw.Fit(degseq,xmin=1)

    fig = plt.figure(figsize=(6,4))
    # degr = [i for i in degrees if i > 0]
    bin_edges = np.logspace(np.log10(min(degseq)), np.log10(max(degseq)), num=10)

    # "x" should be midpoint (IN LOG SPACE) of each bin
    log_be = np.log10(bin_edges)

    x = 10**((log_be[1:] + log_be[:-1])/2)

    x1 = np.logspace(0, np.log10(max(degseq))) # the max is the log(Max_Degree)
    y1 = x1 ** -fit.power_law.alpha #Alpha value From above cell
    plt.plot(x1, y1)

    density, _ = np.histogram(degseq, bins=bin_edges, density=True)

    plt.loglog(x, density, marker='o', linestyle='none')
    plt.xlabel(r"Degree $k$", fontsize=16)
    plt.ylabel(r"$P(k)$", fontsize=16)

    # remove right and top boundaries because they're ugly
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    # Show the plot
    plt.show()

