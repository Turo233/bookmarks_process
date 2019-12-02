import os.path
import logging
import re
from collections import OrderedDict, defaultdict
from pprint import pprint

import tornado.ioloop
import tornado.web

NAME_RE = r".*>(.*?)<.*"
HREF_RE = r"<DT><A HREF=\"(.*?)\""
FILE_PATH = "/Users/lin/Documents/bookmarks.html"
BKS = defaultdict(OrderedDict)


class Node:
    def __init__(self, name=None, value=None, res=None, prev=None, next=None):
        self.name, self.value, self.res, self.prev, self.next = name, value, res, prev, next

def gen_directory_2(node=None):
    if node is None:
        with open(FILE_PATH) as f:
            bookmarks = [b.strip() for b in f.readlines()]
        node = Node('root', bookmarks, BKS)
        node.prev = node
    bms = node.value
    for line_index in range(len(bms)):
        line = bms[line_index]
        if line.startswith('<DL'):
            c_name = re.match(NAME_RE, bms[line_index-1]).group(1)
            node.res[c_name] = {}
            new_node = Node(c_name, bms[line_index+1:], node.res[c_name], node)
            gen_directory_2(new_node)
            return
        elif line.startswith('<DT><A'):
            line_name = re.match(NAME_RE, line).group(1)
            href_name = re.match(HREF_RE, line).group(1)
            node.res[f"{line_name[:15]}-{href_name}"] = line

        elif line.startswith('</DL'):
            cur_name = re.match(NAME_RE, bms[line_index-1]).group(1)
            node = node.prev


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        gen_directory_2()

        return self.render('templates/index.html', bookmarks=BKS['Bookmarks']['书签'])


if __name__ == "__main__":
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

    application = tornado.web.Application([
        (r"/", MainHandler),
    ], **settings)
    application.listen(5000)
    tornado.ioloop.IOLoop.current().start()
