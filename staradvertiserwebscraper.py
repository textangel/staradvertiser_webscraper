from bs4 import BeautifulSoup, NavigableString
import urllib2,sys,datetime,json,re
from StdSuites.Type_Names_Suite import null
from docutils.nodes import paragraph

#Web header to bypass robots.txt
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8'}

#Uses BeautifulSoup to get a navigable HTML Soup object containing the HTML for a given website
def getHTMLSoupFromAddress(address):
    # address = "http://www.staradvertiser.com/2017/08/08/breaking-news/u-s-scientists-contradict-trumps-climate-claims/"
    req = urllib2.Request(address, headers=hdr)
    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()    
    html = page.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# Gets a list of dates from startdate to enddate
def getAllDates(startdate,enddate):
    #note: check if enddate > startdate for robustness
    d = startdate
    dates = []
    while d <= enddate:
        dates += [d.strftime("%Y/%m/%d")]
        d += datetime.timedelta(days=1)
    print dates
    return dates

#Removes formatted quotes and replaces them with regular quotes
def clean(text):
    text = re.sub(u"(\u2018|\u2019)", "'", text)
    text = re.sub(u"(\u201c|\u201d)", '"', text)
    return text

#Gets the title, author, date, and text for a news article at a certian web address.
def getDataFromAddress(address):
    soup = getHTMLSoupFromAddress(address)
    data = {}
    data['title'] = clean(soup.h1.string).replace("\n","")
    data['author'] = clean(soup.find("div",class_="custom_byline").get_text()).replace("\n","")
    data['date'] = clean(soup.find("div",class_="custom_byline postdate").get_text()).replace("\n","")
    text_data = soup.find("div", id = "story-section").find_all('p')
    paragraphs = ""
    for x in text_data:
        if x.string != None:
#             print x.string + "\n\n "
            paragraphs = paragraphs + (x.string) + " \n "
    
    data['text'] = clean(paragraphs)
    json_data = json.dumps(data)
    return json_data

#Gets all the urls for the top headlines of the Star Advertiser for a given date
def getAllUrlsFromDate(address= "http://www.staradvertiser.com/2017/08/08/"):
    soup = getHTMLSoupFromAddress(address)
    urls = []
    for sibling in soup.find("h3", string = re.compile("Top Headlines")).next_siblings:
        if sibling.name == "ul":
            a = sibling.find('a')
            if a != None:
                urls = urls + [a.get('href')]
        if sibling.name == "h3": break
#     print urls
    return urls

#Gets all the data from every top headline article for a given date in the newspaper
def getAllDataFromDate(date):
    urls = getAllUrlsFromDate("http://www.staradvertiser.com/"+date)
    urldate = datetime.datetime.strptime(date, "%Y/%m/%d").strftime("%Y_%m_%d")
#     for url in urls:
#         jsonArticleData = getDataFromAddress(url)
#         print jsonArticleData
    try:
        
        file = open("./docs/Star_advertiser_"+urldate,"w+") 
        print "Writing file ./docs/Star_advertiser_"+urldate
        for url in urls:
            jsonArticleData = getDataFromAddress(url)
            file.write(jsonArticleData)
            file.write("\n\n")
        file.close() 
        print "Finished writing file ./docs/Star_advertiser_"+urldate+"\n\n"
    except:
        print "Unexpected error:", sys.exc_info()[0]

yesterday = datetime.date.today() - datetime.timedelta(days=1)
last_updated_date = datetime.date(2017,02,19)

#Gets all newspaper article data between two dates
def getAllData(startdate = last_updated_date , enddate=yesterday):
    allDates = getAllDates(startdate, enddate)
    for date in allDates:
        getAllDataFromDate(date)

getAllData()
