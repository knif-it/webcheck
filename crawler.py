
# crawler.py - definition of Link class for storing the crawled site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""General module to do site-checking. This module contains the Site class
containing the state for the crawled site and some functions to access and
manipulate the crawling of the website. This module also contains the Link
class that holds all the link related properties."""

import config
import debugio
import urlparse
import robotparser
import schemes
import parsers
import re
import time

class Site:
    """Class to represent gathered data of a site.

    The available properties of this class are:

      linkMap    - a map of urls to link objects
      base       - a url that points to the base of the site
   """

    def __init__(self):
        """Creates an instance of the Site class and initializes the
        state of the site."""
        # list of internal urls
        self._internal_urls = []
        # list of regexps considered external
        self._external_res = []
        # list of regexps matching links that should not be checked
        self._yanked_res = []
        # map of scheme+netloc to robot handleds
        self._robotparsers = {}
        # a map of urls to Link objects
        self.linkMap = {}

    def add_internal(self,url):
        """Add the given url and consider all urls below it to be internal.
        These links are all marked for checking with the crawl() function."""
        if url not in self._internal_urls:
            self._internal_urls.append(url)

    def add_external_re(self,exp):
        """Adds the gived regular expression as a pattern to match external
        urls."""
        self._external_res.append(re.compile(exp,re.IGNORECASE))

    def add_yanked_re(self,exp):
        """Adds the gived regular expression as a pattern to match urls that
        will not be checked at all."""
        self._yanked_res.append(re.compile(exp,re.IGNORECASE))

    def _is_internal(self,link):
        """Check whether the specified url is external or internal.
        This uses the urls marked with add_internal() and the regular
        expressions passed with add_external_re()."""
        res = False
        # check that the url starts with an internal url
        if config.BASE_URLS_ONLY:
            # the url must start with one of the _internal_urls
            for i in self._internal_urls:
                res |= (i==link.url[:len(i)])
        else:
            # the netloc must match a netloc of an _internal_url
            for i in self._internal_urls:
                res |= (urlparse.urlsplit(i)[1]==link.netloc)
        # if it is not internal now, it never will be
        if not res:
            return False
        # check if it is external through the regexps
        for x in self._external_res:
            # if the url matches it is external and we can stop
            if x.search(link.url) is not None:
                return False
        return True

    def _get_robotparser(self,link):
        """Return the proper robots parser for the given url or None if one
        cannot be constructed. Robot parsers are cached per scheme and
        netloc."""
        # only some schemes have a meaningful robots.txt file
        if link.scheme != "http" and link.scheme != "https":
            debugio.debug("crawler._get_robotparser() called with unsupported scheme (%s)" % link.scheme)
            return None
        # split out the key part of the url
        location = urlparse.urlunsplit((link.scheme, link.netloc, "", "", ""))
        # try to create a new robotparser if we don't already have one
        if not self._robotparsers.has_key(location):
            debugio.info("  getting robots.txt for %s" % location)
            self._robotparsers[location] = None
            try:
                rp=robotparser.RobotFileParser()
                rp.set_url(urlparse.urlunsplit((link.scheme, link.netloc, "/robots.txt", "", "")))
                rp.read()
                self._robotparsers[location] = rp
            except TypeError:
                pass
        return self._robotparsers[location]

    def _is_yanked(self,link):
        """Check whether the specified url should not be checked at all.
        This uses the regualr expressions passed with add_yanked_re() and the
        robots information present."""
        # check if it is yanked through the regexps
        for x in self._yanked_res:
            # if the url matches it is yanked and we can stop
            if x.search(link.url) is not None:
                return "yanked"
        # check if we should avoid external links
        if not link.isinternal and config.AVOID_EXTERNAL_LINKS:
            return "external avoided"
        # skip schemes not haveing robot.txt files
        if link.scheme != "http" and link.scheme != "https":
            return False
        # skip robot checks for external urls
        # TODO: make this configurable
        if not link.isinternal:
            return False
        # check robots for remaining links
        rp = self._get_robotparser(link)
        if rp is not None and not rp.can_fetch('webcheck',link.url):
            return "robot restriced"
        # fall back to allowing the url
        return False

    def _get_link(self,url):
        """Return a link object for the given url.
        This function checks the map of cached link objects for an
        instance."""
        # clean the url (remove fragment)
        url = urlparse.urldefrag(url)[0]
        # check if we have an object ready
        if self.linkMap.has_key(url):
            return self.linkMap[url]
        # create a new instance
        return Link(self,url)

    def crawl(self):
        """Crawl the website based on the urls specified with
        add_internal()."""
        # TODO: have some different scheme to crawl a site (e.g. separate
        #       internal and external queues, threading, etc)
        tocheck = []
        for u in self._internal_urls:
            tocheck.append(self._get_link(u))
        # repeat until we have nothing more to check
        while len(tocheck) > 0:
            debugio.debug("crawler.crawl(): items left to check: %d" % len(tocheck))
            # choose a link from the tocheck list
            link=tocheck.pop(0)
            # skip link it there is nothing to check
            if link.isyanked or link.isfetched:
                continue
            # fetch the link's contents
            link.fetch()
            # add children to tocheck
            for child in link.children:
                if not child.isyanked and not child.isfetched and not child in tocheck:
                    tocheck.append(child)
            # add embedded content
            for embed in link.embedded:
                if not embed.isyanked and not embed.isfetched and not embed in tocheck:
                    tocheck.append(embed)
            # sleep between requests if configured
            if config.WAIT_BETWEEN_REQUESTS > 0:
                debugio.debug('sleeping %s seconds' %  config.WAIT_BETWEEN_REQUESTS)
                time.sleep(config.WAIT_BETWEEN_REQUESTS)
        # build the list of urls that were set up with add_internal() that
        # do not have a parent (they form the base for the site)
        bases = [ self.linkMap[self._internal_urls[0]].follow_link(True) ]
        for u in self._internal_urls[1:]:
            l = self.linkMap[u].follow_link(True)
            # if the link has no parent add it to the result list
            if len(l.parents) == 0:
                bases.append(l)
        # do a breadth first traversal of the website to determin depth and
        # figure out page children
        tocheck = []
        for link in bases:
            link.depth = 0
            tocheck.append(link)
        # repeat until we have nothing more to check
        while len(tocheck) > 0:
            debugio.debug("crawler.crawl(): items left to check: %d" % len(tocheck))
            # choose a link from the tocheck list
            link = tocheck.pop(0)
            # figure out page children
            for child in link._pagechildren():
                # skip children already in our list or the wrong depth
                if child in tocheck or child.depth != link.depth+1:
                    continue
                tocheck.append(child)
        # set some compatibility properties
        # TODO: figure out a better way to get to this to the plugins
        self.base = bases[0].url

class Link:
    """This is a basic class representing a url.

    Some basic information about a url is stored in instances of this class:

      url        - the url this link represents
      scheme     - the scheme part of the url
      netloc     - the netloc part of the url
      path       - the path part of the url
      query      - the query part of the url
      parents    - list of parent links (all the Links that link to this page)
      children   - list of child links (the Links that this page links to)
      pagechildren - list of child pages, including children of embedded elements
      embedded   - list of links to embeded content
      depth      - the number of clicks from the base urls this page to find
      isinternal - whether the link is considered to be internal
      isyanked   - whether the link should be checked at all
      isfetched  - whether the lis is fetched already
      ispage     - whether the link represents a page
      mtime      - modification time (in seconds since the Epoch)
      size       - the size of this document
      mimetype   - the content-type of the document
      title      - the title of this document
      author     - the author of this document
      status     - status of fetching this url (not None indicates a problem)
      redirectdepth - the number of this redirect (=0 not a redirect)
   """

    def __init__(self, site, url):
        """Creates an instance of the Link class and initializes the
        documented properties to some sensible value."""
        # store a reference to the site
        self.site = site
        # split the url in useful parts and store the parts
        (self.scheme, self.netloc, self.path, self.query) = urlparse.urlsplit(url)[0:4]
        # store the url (without the fragment)
        url=urlparse.urlunsplit((self.scheme, self.netloc, self.path, self.query, ""))
        self.url=url
        # ensure that we are not creating something that already exists
        assert not self.site.linkMap.has_key(url)
        # store the Link object in the linkMap
        self.site.linkMap[url] = self
        # deternmin the kind of url (internal or external)
        self.isinternal = self.site._is_internal(self)
        # check if the url is yanked
        self.isyanked = self.site._is_yanked(self)
        # initialize some properties
        self.parents = []
        self.children = []
        self.pagechildren = None
        self.embedded = []
        self.depth = None
        self.isfetched = False
        self.ispage = False
        self.mtime = None
        self.size = None
        self.mimetype = None
        self.title = None
        self.author = None
        self.status = None
        self.redirectdepth = 0

    def add_child(self, child):
        """Add a link object to the child relation of this link.
        The reverse relation is also made."""
        # convert the url to a link object if we were called with a url
        if type(child) is str:
            child = self.site._get_link(child)
        # add to children
        if child not in self.children:
            self.children.append(child)
        # add self to parents of child
        if self not in child.parents:
            child.parents.append(self)

    def add_embed(self, link):
        """Mark the given link object as used as an image on this page."""
        # convert the url to a link object if we were called with a url
        if type(link) is str:
            link = self.site._get_link(link)
        # add to embedded
        if link not in self.embedded:
            self.embedded.append(link)
        # add self to parents of embed
        if self not in link.parents:
            link.parents.append(self)

    def add_problem(self, problem):
        """Indicate that something went wrong while retreiving this link."""
        self.status=problem

    def fetch(self):
        """Attempt to fetch the url (if isyanked is not True) and fill in link
        attributes (based on isinternal)."""
        # fully ignore links that should not be feteched
        if self.isyanked:
            debugio.info("  %s" % self.url)
            debugio.info("    "+self.isyanked)
            return
        # see if we can import the proper module for this scheme
        schememodule = schemes.get_schememodule(self.scheme)
        if schememodule is None:
            self.isyanked="unsupported scheme ("+self.scheme+")"
            debugio.info("  %s" % self.url)
            debugio.info("    "+self.isyanked)
            return
        # FIXME: figure out which mimetypes to support before completely
        #        fetching document in memory
        # FIXME: figure out some way to communicate accepted mimetypes from
        #        parsers to schemes (or have first scheme method return some
        #        kind of handle) fetch the content
        debugio.info("  %s" % self.url)
        content=schememodule.fetch(self)
        self.isfetched = True
        # skip parsing of content if we were returned nothing
        if content is None:
            return
        # find a parser for the content-type
        parsermodule = parsers.get_parsermodule(self.mimetype)
        if parsermodule is None:
            debugio.debug("crawler.Link.fetch(): unsupported content-type: %s" % self.mimetype)
            return
        # parse the content
        parsermodule.parse(content,self)

    def follow_link(self,delifunref=False):
        """If this link represents a redirect return the redirect target,
        otherwise return self. If delifunref is set this link is discarded
        if it has no parents."""
        # FIXME: add checking for loops
        if (self.redirectdepth == 0) or (len(self.children) == 0):
            return self
        # remove link if this is the only place that it's used
        if (len(self.parents) == 0):
           # remove me from the linkMap
           del self.site.linkMap[self.url]
           # remove me from parents of child
           self.children[0].parents.remove(self)
        return self.children[0].follow_link(delifunref)

    def _pagechildren(self):
        """Determin the page children of this link, combining the children of
        embedded items and following redirects."""
        # if we already have pagechildren defined we're done
        if self.pagechildren is not None:
            return self.pagechildren
        self.pagechildren = []
        # add my own children, following redirects
        for child in self.children:
            # follow redirects
            child=child.follow_link()
            # skip children we already have
            if child in self.pagechildren:
                continue
            # set depth of child if it is not already set
            if child.depth is None:
                child.depth = self.depth+1
            # add child pages to out pagechildren
            if child.ispage:
                self.pagechildren.append(child)
        # add my embedded element's children
        for embed in self.embedded:
            # set depth of embed if it is not already set
            if embed.depth is None:
                embed.depth = self.depth
            # merge in children of embeds
            for child in embed._pagechildren():
                # skip children we already have
                if child in self.pagechildren:
                    continue
                # add it to our list
                self.pagechildren.append(child)
        # return the results
        return self.pagechildren
