"""

 Webcheck Configuration file
 Edit this file to your choosing.  This is just a regular Python module, so
 if you want to do something fancy with it, go right ahead. Just make sure
 that all variables are defined and have an appropriate value .

"""


# if this is true, webcheck will consider external all links that do not start in 
# the same directory level as the base url.  For example, given
# webcheck http://www.myhost.com/~me/
# 'http://www.myhost.com/~me/stuff/index.html' would be considered internal while
# 'http://www.myhost.com/index.html' would be considered external.
# The default is false (0). note this can be overriden with the -b command-line
# flag
BASE_URLS_ONLY=0

# This is a (Python) list of URLs that should not be explored.  This can also
# be passed to webcheck via the -x command line switch.  Note this should be a
# VALID REGULAR EXPRESSION.  See also YANKED_URLS below.
EXCLUDED_URLS = [r'.*\.gif',r'.*\.tar\.gz',r'.*\.jpeg',r'.*\.jpg',
		 r'http://www.mired.org/cgi-bin/', r'http://www.mired.org/ATCPFAQ/']

# This is like EXCLUDED_URLS, but YANKED_URLS are not checked at all.  Also
# you can use the -y command line switch.
# When using the below parameter, make sure that the regular expressions are
# raw Python strings (beginning quote preceded with an "r").  Regular expressions
# are case insensitive.
YANKED_URLS = [r'http://www.amazon.com/exec/obidos/',
	       r'http://www.mired.org/home/mwm/&me;.txt']

# Normally webcheck will check links to "external" sites at the top level to
# ensure that your pages don't refer to broken links that are not at your
# site. However, you may not want this.  Setting this option to 1 will cause
# webcheck to not check external links.  Note a link that is part of the. This
# can also be set with the command-line -a switch
#
# EXCLUDED_URLS list is considered external
AVOID_EXTERNAL_LINKS = 0

# Currently, Webcheck can checks http:, ftp:, and file:, schemes.  However, you may
# want to avoid certain schemes (such as file: or ftp:).  Remove the scheme
# from this list and Webcheck will avoid it.  Avoided URLs are treated as external
# Default is to not avoid any.
# Examples:
#SCHEMES = ['http']
#SCHEMES = ['http','ftp','file']
SCHEMES = ['http','ftp']



# You can define proxies for the individual schemes above.  The PROXIES config
# variable is a python dictionary or 'None', for example:
# PROXIES = {'http':'http://localhost:3128'}
PROXIES = None
# Note: according to the urllib documentation, you should also be able to set
# proxies according to your system's environment variables, for example:
# $ HTTP_PROXY='http://localhost:3128' ; export HTTP_PROXY # using Bourne Shell
# $ FTP_PROXY='http://localhost:3128' ; export FTP_PROXY
# proxies in the configuration take precedence over environment settings

# You can add headers to the requests to provide finer control over what is being
# fetched. This is a list of pairs. Each pair is a header, and the value it should
# have. For example:
#HEADERS = [('Cache-Control', 'no-cache'), ('Pragma', 'no-cache')]
# will turn off all caching.
HEADERS = None


# hostnames (for example, www.myhost.com) which are to be considered local to
# your site.  Note that by default, the base URL of your site is considered
# local.  This can also be passed via command-line (see documentation for details
HOSTS = []


# Directory where files generated by webcheck will be placed.  This can also be
# specified via the -o command-line flag.
OUTPUT_DIR = '.'

# When listing a broken link in its published report, Webcheck can either make the
# broken link 'active' or simply list the URL.  Most users will probably not
# want the broken link to be active.
ANCHOR_BAD_LINKS = 1

# Usually, Webcheck will processs a URL and immediately move on to the next one.
# However, on some loaded systems, it may be more desirable to have Webcheck wait
# a while between requests.  This option should be set to any non-negative number
# (in seconds).  This can also be set using the command-line -w <secs> flag.
WAIT_BETWEEN_REQUESTS = 0

# When Webcheck encounters a 301 or 302 response from the server, it
# needs to decide how many times it will follow the indications of the
# server. By setting this option, you may change it to your
# tastes. Setting it to -1 means "infinite redirection" (don't say I
# didn't warn you, when your sysadm tries to make you eat the 10^6
# network logs you produced and he printed... :)
REDIRECT_DEPTH = 5

# Debug level.  For normal output, set to 1.  The higher the number, the more
# output.  A setting of 0 produces no output. 
DEBUG_LEVEL = 1

################ The section below is for report plugins  ################

# This is the list of report plugins to display. The elements are strings and
# there should be a corresponding .py file in the WEBCHECKHOME/reports directory
# else bad things will occur ;-).  Place in the order for which you would like to
# see them in the navigation bar.
# Note: Do not include the 'problems' report as it will appear (last) on all
# reports automatically
PLUGINS = ['sitemap',
	   'badlinks',
	   'images',
	   'whatsold',
	   'whatsnew',
	   'slow',
	   'notitles',
	   'external',
	   'notchkd']
	   
# This is a URL (absolute or relative) of a level 1 Cascading Stylesheet to be
# used in all reports.  See the default webcheck.css as well as the HTML source
# for ideas on making your own .css for Webcheck.
STYLESHEET = 'file:///usr/share/webcheck/webcheck.css'

##### The Navigation (menu) frame/page ############
NAVBAR_FILENAME    = 'navbar.html'
NAVBAR_WIDTH = '150'
NAVBAR_PADDING = 4
NAVBAR_SPACING = 0

MAIN_FILENAME      = 'index.html'
OVERWRITE_FILES    = 0

# url to logo (image) shown on all pages.  If you change this you will also
# want to change the LOGO_ALT option below
LOGO_HREF="webcheck.png"

##### Configuratin for specific plugins #####
REPORT_SITEMAP_LEVEL = 5 # How many levels deep to display the site map

# number of columns in thumbnail image page
REPORT_IMAGES_COLS=5
# width of thumbnail images
REPORT_IMAGES_WIDTH=100
# height of thumbnail images
REPORT_IMAGES_HEIGHT=100

REPORT_WHATSOLD_URL_AGE = 700
REPORT_WHATSNEW_URL_AGE = 7

REPORT_SLOW_URL_SIZE = 76

