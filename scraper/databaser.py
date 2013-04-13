import os
import glob
import json
from dateutil.parser import parse

from models import Course, Class, Location
from django.db import transaction

def load_course_data():
    paths = set(glob.glob(os.path.join(os.getcwd(), "scraper/data/*courses.json")))
    with transaction.commit_on_success():
        coreqlist = []
        for fname in paths:
            print fname
            with open(fname, "r") as f:
                courses = json.load(f)
            for c in courses:
                a, created = Course.objects.get_or_create(subject=c["subject"], number=c["course"])
                a.prereqs=c.get("prereqs", "")
                a.coreq=None
                a.title=c["title"]
                a.description=c["description"]
                a.credits=c["credits"]
                a.save()

        for x in coreqlist:
            try:
                temp = x["coreq"].split()
                c1 = Course.objects.get(number=x["course"], subject=x["subject"])
                c2 = Course.objects.get(number=temp[1], subject=temp[0])
                if not c1.coreq and not c2.coreq:
                    c1.coreq = c2
                    c2.coreq = c1
                    c1.save()
                    c2.save()
                elif not c2.coreq and c2.coreq:
                    print "AHH", c1, c2
            except Exception as e:
                print e, temp, (x["subject"], x["course"])


def load_class_data():
    both = set(glob.glob(os.path.join(os.getcwd(), "scraper/data/*.json")))
    courses = set(glob.glob(os.path.join(os.getcwd(), "scraper/data/*courses.json")))
    with transaction.commit_on_success():
        for fname in both ^ courses:
            print fname
            with open(fname, "r") as f:
                classes = json.load(f)

            for c in classes:
                a, created = Class.objects.get_or_create(crn=c["crn"])
                a.campus=c["campus"]
                a.course=Course.objects.get(number=c["course"], subject=c["subject"])
                a.seats=c["seats"]
                a.enrolled=c["enrolled"]
                a.instructor=c["instructor"]
                a.section=c["section"]
                a.save()

                for x in c["location"]:
                    b = Location(
                            c = a,
                            online = x["online"],
                            start_date = parse(x["start_date"]),
                            end_date = parse(x["end_date"]),
                            start_time = parse(x["start_time"]) if x["start_time"] else None,
                            end_time = parse(x["end_time"]) if x["end_time"] else None,
                            days_of_week = x["days_of_week"],
                            building = x["building"],
                            room = x["room"],
                        )
                    b.save()

if __name__ == "__main__":
    load_course_data()
    load_class_data()