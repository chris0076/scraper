import urllib
import urllib2
import pprint
import json
import multiprocessing
import os

subjects = {
    "ACCT":    "Accounting",
    "ANTH":    "Anthropology",
    "ARAB":    "Arabic",
    "ARED":    "Art Education",
    "ART":     "Art",
    "ARTS":    "Interdisciplinary Fine Arts",
    "ASTR":    "Astronomy",
    "ATEP":    "Athletic Training",
    "BIOL":    "Biology",
    "BUSA":    "Business Administration",
    "CGLO":    "Contemporary Global Issues",
    "CHEM":    "Chemistry",
    "CHIN":    "Chinese",
    "COMM":    "Communications",
    "COUN":    "Counseling",
    "CRJU":    "Criminal Justice",
    "CSCI":    "Computer Science",
    "DVRS":    "Diversity",
    "ECDV":    "Early Childhood Development",
    "ECED":    "Early Childhood Education",
    "ECON":    "Economics",
    "EDGE":    "Gifted Education",
    "EDL":     "Educational Leadership",
    "EDUC":    "Education",
    "ENGL":    "English",
    "ENGR":    "Engineering",
    "ENST":    "Environmental Studies",
    "ESCI":    "Environmental Science",
    "ESLC":    "ESL Communication",
    "ESLO":    "Class. Comm. & College Orient.",
    "ESLR":    "ESL Reading",
    "ESLV":    "ESL Vocabulary",
    "ESLW":    "ESL Writing",
    "FILM":    "Film Studies",
    "FINC":    "Finance",
    "FREN":    "French",
    "GEOG":    "Geography",
    "GEOL":    "Geology",
    "GERO":    "Gerontology",
    "GISC":    "Geographic Information Science",
    "GRMN":    "German",
    "HIST":    "History",
    "HSDA":    "Human Services Delivery & Adm",
    "ISCI":    "Integrated Science",
    "ITAL":    "Italian",
    "JAPN":    "Japanese",
    "JOUR":    "Journalism",
    "KREN":    "Korean",
    "LART":    "Language Arts",
    "LATN":    "Latin",
    "MAED":    "Math Education",
    "MATH":    "Mathematics",
    "MDST":    "Media Studies",
    "MGED":    "Middle Grades Education",
    "MGMS":    "Middle Grades Math/Science",
    "MGMT":    "Management",
    "MILS":    "Military Science",
    "MKTG":    "Marketing",
    "MLAN":    "Modern Languages",
    "MLCS":    "Mathematical Literacy",
    "MUAP":    "Applied Music",
    "MUED":    "Music Education",
    "MUSC":    "Music",
    "NDPT":    "Physical Therapy",
    "NURS":    "Nursing",
    "PARA":    "Paralegal",
    "PHED":    "Physical Education",
    "PHIL":    "Philosophy",
    "PHYS":    "Physics",
    "POLS":    "Political Science",
    "PSYC":    "Psychology",
    "READ":    "Reading",
    "RELG":    "Religion",
    "RSCH":    "Research",
    "RUSS":    "Russian",
    "SCI":     "Science",
    "SIED":    "Science Education",
    "SOCI":    "Sociology",
    "SOWK":    "Social Work",
    "SPAN":    "Spanish",
    "SPED":    "Special Education",
    "THEA":    "Theater",
    "THS":     "Thesis",
    "TMGT":    "Technology Management",
    "UNIV":    "University"
}

def find_element(element, text, element2=None):
    start = text.index(element) + len(element)
    if element2 is None:
        end = text.index(element, start)
    else:
        end = text.index(element2, start)
    return start, end

def find_first_block(text):
    element = "<SMALL>ROOM</SMALL>"
    start = text.index(element) + len(element)

    end = text.index("ddseparator", start)
    return start, end

find_next_block = lambda text: find_element("ddseparator", text)
find_next_small = lambda text: find_element("<SMALL>", text, element2="</SMALL>")

def get_all_small_data(text):
    data = []
    while text:
        try:
            start, end = find_next_small(text)
            data.append(text[start:end])
            text = text[end:]
        except ValueError:
            text = ''
    return data

def strip_data(data):
    if type(data) == dict:
        for key, item in data.items():
            try:
                data[key] = item.strip()
            except AttributeError:
                data[key] = strip_data(item)
    elif type(data) in (list, tuple, set):
        for i, item in enumerate(data):
            try:
                data[i] = item.strip()
            except AttributeError:
                data[i] = strip_data(item)
    elif type(data) == str:
        return data.strip()
    return data

def clean_data(data):
    final = dict()
    while "Seats:" not in data[-1]:
        data.pop()

    start = data[0].index(">") + 1
    end =  data[0].index("<", start)
    final["crn"] = data[0][start:end]
    final["subject"] = data[1]
    final["course"] = data[2]
    final["section"] = data[3]
    final["credits"] = data[4]
    final["title"] = data[5]

    start = data[6].index(">") + 1
    final["campus"] = data[6][start:]

    # special
    final["location"] = []
    idx = 7
    while "Instructor:" not in data[idx]:
        a = dict()
        a["start_date"] = data[idx]
        a["end_date"] = data[idx+1]
        if "Online" in data[idx+2]:
            a["online"] = True
            a["days_of_week"] = None
            a["start_time"] = None
            a["end_time"] = None
            a["room"] = None
            a["building"] = None
            idx += 3
        else:
            a["online"] = False
            a["days_of_week"] = data[idx+2]
            try:
                a["start_time"], a["end_time"] = data[idx+3].split("-")
            except ValueError:
                # TBA
                a["start_time"] = a["end_time"] = "00:00am"
            a["building"] = data[idx+4]
            a["room"] = data[idx+5]
            idx += 6
        final["location"].append(a)

    final["instructor"] = data[-3].split("</B>")[-1]
    final["enrolled"] = data[-2].split("</B>")[-1]
    final["seats"] = data[-1].split("</B>")[-1]
    return strip_data(final)

def parse_course_list(text):
    data = []
    start, end = find_first_block(text)
    data.append(clean_data(get_all_small_data(text[start:end])))
    text = text[end:]
    while text:
        try:
            start, end = find_next_block(text)
            data.append(clean_data(get_all_small_data(text[start:end])))
            text = text[end:]
        except ValueError:
            text = ''
    return data

def parse_requisites(pre, text):
    start = text.index(pre+"requisites: ")
    text = text[start:]
    start, end = find_element("<BR>", text)
    text = text[start:end]
    for i in xrange(text.count("</A>")):
        start = text.index("<A HREF")
        end = text.index(">", start)+1
        text = text[:start]+text[end:]
    text = text.replace("</A>", '')
    return text.strip()


# def parse_prereq_classes(text):
#     # a = text.split(" - Semester level  ")
#     a = [x for x in text.split() if x not in {"-", "Semester", "level", "Minimum", "Grade", "of"}]
#     final = [[]]
#     state = "start"
#     for i, item in enumerate(a):
#         if state == "start":
#             if item.startswith("("):
#                 final.append([item[1:]])
#                 state = "class"
#             else:
#                 final[-1].append(item)
#         if state == "class"

def parse_course_description(text):
    a = dict()
    start = text.index("colgroup")
    text = text[start:]

    start, end = find_element(">", text, "</TD>")
    a["title"] = text[start:end]
    text = text[end:]

    start, end = find_element('"ntdefault">', text, "<BR>")
    a["description"] = text[start:end]
    text = text[end:]
    start, end = find_element('<BR>', text, "Credit")
    a["credits"] = text[start:end]

    start, end = find_element("</SPAN>", text, "<BR>")
    a["levels"] = [x.split(" - ") for x in text[start:end].split(",")]
    text = text[end:]

    start, end = find_element("</SPAN>", text, "<BR>")
    temp = text[start:end].split(",")
    for i, item in enumerate(temp):
        try:
            newstart, newend = find_element(">", item, "</A>")
        except:
            newstart = 0
            newend = len(item)
        temp[i] = item[newstart:newend]
    a["scheduletypes"] = temp
    text = text[end:]

    try:
        a["prereqs"] = parse_requisites("Pre", text)
    except ValueError:
        pass

    try:
        a["coreq"] = parse_requisites("Co", text)
    except ValueError:
        pass
    return strip_data(a)

def run(key):
    try:
        values = {
            "stvterm_code": "201308",
            "stvptrm_code": "All",
            "ssbsect_subj_code": key,
            "ssbsect_crse_numb": "All",
            "core_area": "All",
            "stvcamp_code": "All",
            "gtvinsm_code": "All",
            "stvschd_code": "All",
            "ssrmeet_begin_time": "0000",
            "ssrmeet_end_time": "2359",
            "sirasgn_pidm": "0",
            "cbutton": "Search",
        }
        url = "https://ungssb.ung.edu/pls/ungprod/COM_F02_PKG.course_search"
        urldata = urllib.urlencode(values)
        print "Downloading %s Data" % key
        req = urllib2.Request(url, urldata)
        response = urllib2.urlopen(req, None, 30)

        print "Parsing %s Data" % key
        temp = parse_course_list(response.read())
        with open(os.path.join(os.getcwd(), "scraper/data/%s_courses.json") % key, "w") as f:
            json.dump(temp, f, sort_keys=True, indent=4, separators=(',', ': '))

        courseset = set(course["course"] for course in temp)
        courses = []
        for course in courseset:
            print "    Downloading %s %s Data" % (key, course)
            url2 = "https://ungssb.ung.edu/pls/ungprod/bwckctlg.p_disp_course_detail"
            values2 = {
                "cat_term_in": values["stvterm_code"],
                "subj_code_in": key,
                "crse_numb_in": course,
            }
            urldata2 = urllib.urlencode(values2)
            req2 = urllib2.Request(url2, urldata2)
            response2 = urllib2.urlopen(req2, None, 30)
            temp = parse_course_description(response2.read())
            temp["course"] = course
            temp["subject"] = key
            print "    Parsing %s %s Data" % (key, course)
            courses.append(temp)
        with open(os.path.join(os.getcwd(), "scraper/data/%s_courses.json") % key, "w") as f:
            json.dump(courses, f, sort_keys=True, indent=4, separators=(',', ': '))
    except urllib2.URLError:
        return key

def run_all(listing=None):
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    if listing:
        err = [x for x in listing if x in subjects]
    else:
        err = subjects.keys()

    while len(err):
        temp = p.map(run, err)
        err = [x for x in temp if x]
    p.close()
    p.join()


if __name__ == "__main__":
    run_all()