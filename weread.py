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



USER_AGENT =  "WeReadImporter"
authentication_url = "http://weread.com/login_action.php"

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


def get_number_of_pages():
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
        list of books, each book is tuple in the format (book title, author).
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
    

    
def get_bookshelf():
    """
    Fetch user's bookshelf.
    
    Args:
        none.
        
    Returns:
    
        A list of tuples containing, for each book, (isbn, title, author)
    """

    url_string = "%s" % (weread_profile_url, )  + "page-%d" 
    total_pages = get_number_of_pages()
    
    print "Total pages: %s" % total_pages
    
    results = []
    
    for i in range(1, total_pages):

        print "Reading page %d..." % i        
        response = urllib2.urlopen(url_string % i)
        print "Read page %d." % i

        page = response.read()    
        results.append(parse_page(page))
    
    return results
    
    
def main(email, password):

    init()
    
    # Login
    if not login(email, password):
        print "Error:  could not login user %s" % (weread_email, )
        exit(1)
    
    books = get_bookshelf()
    
    
if __name__ == '__main__':
    from settings import *
    main(weread_email, weread_password)