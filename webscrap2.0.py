from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re


def pageSoup(url):
    # getting the html code and making it human readable.
    # works only if "url" is the main degree website.
    my_url = r"{}".format(url)
    u_client = uReq(my_url)
    page_soup = soup(u_client.read(), "html.parser")
    u_client.close()
    return page_soup


def get_courses_links(url):
    # getting all the suggested courses for the degree.
    url_list = []
    page_soup = pageSoup(url)
    containers = page_soup.findAll("table", {"class": "t3c"})
    for container in containers:
        courses = container.select("a")
        for i in courses:
            url_list.append(i["href"])
    return fix_links(url_list)


def fix_links(list_url):
    # fixes the url's, that we got from the main site url.
    p = re.compile('\d{5}')
    return [r"https://www.openu.ac.il/courses/" + url[-5:] + ".htm" for url in list_url if p.match(url[-5:]) is not None]


class course:
    def __init__(self, course_url):
        # constructor for the "course" class
        self.url = course_url
        page_soup = pageSoup(course_url)
        title = page_soup.find('h1', {'id': 'course_title'}).text.strip()
        self.course_number = [int(s) for s in title.split() if s.isdigit()][0]
        level_points = page_soup.find_all("strong")[0].text.strip()
        semester_given_url = page_soup.select("a")[3].get('href')[:-5] + str(self.course_number)
        semester_given = pageSoup(semester_given_url)
        self.course_name = ''.join([i if i.isalpha() else " " for i in re.findall('[\w +/.]', title)]).strip()
        self.course_points = [int(s) for s in level_points.split() if s.isdigit()][0]
        self.course_kind = ''.join([i if i.isalpha() else " " for i in re.findall('[\w +/.]', level_points)]).strip()
        self.semester_given = [li.text for li in semester_given.findAll('li')]
        # self.required_cou = self.required_courses()  # see explanation in function

    def __str__(self):
        return "course_number: {} \n course_name: {} \n course_points: {} \n course_kind: {} \n semester_given: {}\n\n"\
            .format(self.course_number,
                    self.course_name,
                    self.course_points,
                    self.course_kind,
                    self.semester_given)

    def __repr__(self):
        return self.__str__()

    def required_courses(self):
        # because of a bug in the site, and because i didn't use try/except yet, this doesnt work on all links.
        # but generally, it works.
        page_soup = pageSoup(self.url)
        required_courses = page_soup.find('div', {'id': 'content'}).select("p")[3]
        courses_urls_list = [i["href"] for i in required_courses.select("a")]
        courses = [course(courses_urls_list[i]) for i in range(len(courses_urls_list))]
        return courses
    recommended_course = self.prereqisites2parts()[2]


courses = get_courses_links(r"https://academic.openu.ac.il/CS/computer/program/AF.aspx")
courses = [course(c) for c in courses]
print(courses)
