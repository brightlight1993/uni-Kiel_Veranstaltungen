# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
import lxml.html
import cssselect
import re
import json
from urlparse import urlparse # for Python2 else below
# from urllib.parse import urlparse  # for Python3



def getBtnsIfNoClassXOnPage(root, searchedCssClass, justRtButtons=False):
    
    if (len(root.cssselect(searchedCssClass)) < 1) or justRtButtons:
        return root.cssselect(".button")
    else :
        return root

def recursivWonder(htmlElement, eventCssClass, website, depth_limes=0 ):
    global scrapedPages, searchedItemsFound, date_addrSet, searchedItemsDropped, visitedPages
    itemCount = 0
    if depth_limes>9 :
        print('!!!!!!!!!!!!!!!!!!!!!!!! cacel Condition reached!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return 0
    else :
        btnLst=getBtnsIfNoClassXOnPage(htmlElement,eventCssClass)
        if(btnLst==htmlElement):
            for j in htmlElement.cssselect(eventCssClass):
                title=j.cssselect('.ce-headline-h4 span')[0].text_content() 
                if title != None and len(title)>2:
                    date_addr= j.cssselect("div.news-list-item__dateline div.news-item__event-date")[0].text_content() 
                    
                    if (date_addr != None) and len(date_addr)>1:
                        date_addr= re.sub(r'\r*\n*\t*(  )*', '',date_addr)
                        if not ((date_addr in date_addrSet) and (title in titleSet)): 
                            data={"title": title, "date_addr": date_addr}
                            dataLst.append(data)
                            #print(date_addr)                
                            scraperwiki.sqlite.save(unique_keys=[], data=data, table_name="events")
                            date_addrSet.add(date_addr)
                            titleSet.add(title)
                            #print("found Item: "+title+"\n"+date_addr)
                            #searchedItemsFound+=1
                            itemCount+=1
                        else:
                            #print('dropping '+title)
                            searchedItemsDropped +=1
                    else:
                        print('date_addr  too short  or not found Type(date_addr)= '+ str(type(date_addr)))
                else:
                    print('title  too short or not found')
            #return True
        btnLst=getBtnsIfNoClassXOnPage(htmlElement, eventCssClass, True)
        if(len(btnLst) > 0):
            trueOrFalseLst = []
            for y in xrange(len(btnLst)):
                btnHref=btnLst[y].get('href')
                if btnHref != None: 
                    if btnHref[0] == '/':
                        nextLink=prtclAndHst+btnHref
                        if not( nextLink in visitedPages):
                            #print(scrapedPages, 'pages scraped, next scraping:', nextLink)
                            visitedPages.add(nextLink)
                            itemCount+= recursivWonder(lxml.html.fromstring(scraperwiki.scrape(nextLink)), eventCssClass, nextLink ,++depth_limes)
                            scrapedPages += 1
                            
                        #print(scrapedPages, "pages scraped")
                        #else :
                           # print('skipping already visited link: '+nextLink)
    print(str(itemCount)+" new Items found under " + website )
    return itemCount

#general Config
url= "https://www.uni-kiel.de/de/veranstaltungen/"
searchedHtmlElement = "div.news-list-item"
hamburgerElementsClass='li.navigation-list__item:nth-child(5)'


# # Read in a page
html = scraperwiki.scrape(url)
scrapedPages = 1
searchedItemsFound=0
searchedItemsDropped=0
date_addrSet = set()
titleSet = set()
dataLst=list()
visitedPages=set()

# get hostname
parsed_uri = urlparse(url )
prtclAndHst = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
#
# # Find something on the page 
root = lxml.html.fromstring(html)
# print(root)
hamburgerElements=root.cssselect(hamburgerElementsClass)
# print(hamburgerElements)
buttons= hamburgerElements[0].cssselect('a') 
#buttons = getBtnsIfNoClassXOnPage(root, searchedHtmlElement, True)
# print(len(buttons))
# for x in buttons:
#     print(x.get('href'))
# print(buttons[0].get('href'))

for x in xrange(len(buttons)):
    href=buttons[x].get('href')
    if href != None:
        if href[0] == '/':
            nextLink=prtclAndHst+href
            if not( nextLink in visitedPages):
                #print('Main: '+str(scrapedPages)+' pages scraped, next scraping: '+ str(nextLink))
                visitedPages.add(nextLink)
                page2=lxml.html.fromstring(scraperwiki.scrape(nextLink))
                scrapedPages += 1
                searchedItemsFound += recursivWonder(page2, searchedHtmlElement, nextLink)
print("Result: "+str(scrapedPages)+"pages Scraped, found "+str(searchedItemsFound)+'Items, dropped '+str(searchedItemsDropped)+'Items, ')
# print(titleSet)
# titleList = list(titleSet)
# date_addrList = list(date_addrSet)
# events=list()
# for t in xrange(len(titleList)):
#     events.append( {
#         'title': titleList[t],
#         'date_addr': date_addrList[t]
#         })
#with open("data_file.json", "w") as write_file:
 #   json.dump(dataLst, write_file)

#print(scraperwiki.sql.select("title from events"))   
 
            
            

    
    
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".
