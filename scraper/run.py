from databaser import load_course_data, load_class_data
from scraper import run_all

def set_up():
    run_all()
    load_course_data()
    load_class_data()


if __name__ == "__main__":
    set_up()