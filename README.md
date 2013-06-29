weread-export
=============

This python script will let you recover all your books from WeRead.

WeRead, initially named iRead, was a Facebook App that became popular around 2008, and let you share the titles of the books you were reading with your friends.  It also served as a bookshelf, where you could keep track of your readings.  

At some point, and after lots of readers (like me...) had invested time and effort using the service, weRead stopped working.  The data can still be accessed through their website, but you can't export your books to any other format or download the list for your own use.

As I had 200+ books in weRead, I wrote this script to recover them in a simple format.

## Dependencies

*  The script has been tested on Python 2.7.3.  I have not tested it in Python 3.
*  No additional libraries are needed.

## Usage

1. From the command line:

    $ python weread.py myemail@email.com password
  
2. As a library:

	import weread

	books = weread.main('myemail@email.com', 'password')
 

## To Do

*  Get profile url directly from web page.
*  Command line options.
*  Output formats.
