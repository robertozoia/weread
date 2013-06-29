# -*- encoding: utf-8 -*-

#
#  This is a quick hack to recover your library from weread.com (previously iRead)
# 

import os
import urllib
import urllib2
import cookielib
import hashlib
import json
import re
import sys



USER_AGENT =  "mybooklibrary"
authentication_url = "http://weread.com/login_action.php"
cmd_line = False

# http://stackoverflow.com/questions/13925983/login-to-website-using-urllib2-python-2-7

def login(email, password):
    """
    Logs into weread website.
    
    Args:
        email (str):    weread user email.
        pass  (str):    user password.
        
    Returns:
        boolean
            True if login succeded, False otherwise
    """
    
    # weread expects password as an md5 hash.
    m = hashlib.md5()
    m.update(password)
    
    payload = {
        'email': email, 
        'pass':  m.hexdigest(),
        'rememberpass': 'remember',
        'actiontype': 'submitform',
    }
    
    data = urllib.urlencode(payload)
    request = urllib2.Request(authentication_url, data)
    response = urllib2.urlopen(request)
    contents = json.loads(response.read())
    
    return (contents.get('status') == 'success')


def init():
    """
    Initializes urllib 
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', USER_AGENT), ]
    urllib2.install_opener(opener)


def get_profile():
    """
    Returns a tuple containing weread username and user number (needed for
    building the weread profile url.
    
    Args:
        none
        
    Returns:
        A string with the url of the user's weRead profile page.
    """
    
    response = urllib2.urlopen("http://weread.com/iread_index.php")

    black_magic = re.compile("My profile\s*<\s*/span>.*<a\s+href=['\"]http://weread.com/profile/(?P<user>.*?)/(?P<number>\d+)[?]src=['\"]\s+class\s*=\s*['\"]smitemtext['\"]\s*>\s*<span\s+class\s*=['\"]smitemtextdisplay['\"]>\s*My\s+books\s*<\s*/span\s*>",re.DOTALL)

    r = black_magic.search(response.read())
    return "http://weread.com/profile/%s/%s/" % r.groups()
    

def get_number_of_pages(weread_profile_url):
    """
    Retrieves the number of pages in the user's bookshelf.
    
    Args:
        user's bookshelf page in html
        
    Returns:
        int
            total number of pages in bookshelf.
    """
    
    page = urllib2.urlopen(weread_profile_url)  
    
    regex = re.compile("['\"]pagination_header_text['\"]\s*>.*of\s+(?P<data>.*)<\s*\/td>")
    return int(regex.findall(page.read())[0])
    

def parse_page(page):
    """
    Parses the bookshelf page and returns a list of books

    Args:
        bookshelf page
    
    Returns:
        list of books, each book is tuple in the format (isbn, book title, author).
    """
 
    # The author is in an anchor tag with class uSAuthorText.
    # The book title is in an anchor tag with class uSTitleText.
    # The isbn can be fetched from the image link, and has class s_previewLinkDiv.
    
    # 
    # Everbody will advice against using regex to parse webpages and use some library
    # like BeautifulSoup or lxml. In this case,beautifulsoup could't parse
    # weread.com page, so raw power had to be used.
    # pythonregex.com is your friend...

    black_magic = re.compile("class\s*=\s*['\"]s_previewLinkDiv\s*['\"]\s*id\s*=['\"]preview_(?P<isbn>.*?)['\"]>.*?class\s*=\s*['\"]uSTitleText.*?[\"'](?:\s*\w+)+[='\"].+?>(?P<title>.*?)<\s*\/a>.*?class\s*=\s*['\"]uSAuthorText.*?[\"'](?:\s*\w+)+[='\"].+?>(?P<author>.*?)<\s*\/a>",re.DOTALL)
    
    r = black_magic.findall(page)
    return r


def get_page_i(weread_profile_url, i):
    """
    Returns books from page i of user profile
    """
    url_string = "%s" % (weread_profile_url, )  + "page-%d"
    response = urllib2.urlopen(url_string % i)
        
    page = response.read()    
    results = parse_page(page)
    return results    


def get_bookshelf():
    """
    Fetch user's bookshelf.
    
    Args:
        none.
        
    Returns:
    
        A list of tuples containing, for each book, (isbn, title, author)
    """
    
    weread_profile_url = get_profile()
    url_string = "%s" % (weread_profile_url, )  + "page-%d" 
    
    if cmd_line:  print("User profile url: %s" %  weread_profile_url)
        
    total_pages = get_number_of_pages(weread_profile_url)
    
    if cmd_line: print("Total pages: %s" % total_pages)
    
    results = []
        
    for i in range(1, total_pages):
        if cmd_line:
            sys.stdout.write("Processing page %d of %d. \r" % (i, total_pages ))
            sys.stdout.flush()

        results += get_page_i(weread_profile_url, i)
    
    if cmd_line:  print()
    
    return results
    
    
def main(email, password):

    init()
    
    # Login
    if not login(email, password):
        print "Error:  could not login user %s" % (weread_email, )
        exit(1)
    
    books = get_bookshelf()
    
    return books
    
    
if __name__ == '__main__':

    import argparse
    import importlib
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="The email associated to your weRead account.")
    parser.add_argument("password", help="Your weRead password.")
    
    parser.parse_args()
    args = parser.parse_args()
    weread_email = args.email
    weread_password = args.password 
    
    cmd_line = True
    books = main(weread_email, weread_password)
    
    for b in books:
        isbn, title, author = b
        print "%s\t%-30s\t%s" % (isbn, author, title)
    
        
