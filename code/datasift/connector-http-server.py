import tornado.ioloop
import tornado.web
import time

global COUNT
COUNT = 0

class MainHandler(tornado.web.RequestHandler):

    def post(self):
        global COUNT
        ts = str(int(time.time()))
        of = "json"
        COUNT += 1
        print "This is the [%d] post request!!" % COUNT
        
        print "The content is [--- %s  ---]" % self.request.body

        if self.request.body == '{}':
                print 'Got {} from DataSift!'

        if 'X-Datasift-Hash' in self.request.headers:
                print 'Got X-Datasift-Hash: ',
                print self.request.headers['X-Datasift-Hash']

        if 'X-Datasift-Hash-Type' in self.request.headers:
                print 'Got X-Datasift-Hash-Type:',
                print self.request.headers['X-Datasift-Hash-Type']

        if 'Content-Encoding' in self.request.headers:
                print 'Got Content-Encoding:',
                of = self.request.headers['Content-Encoding']
                print of

        if 'X-Datasift-Id' in self.request.headers:
                print 'Got X-Datasift-Id:',
                print self.request.headers['X-Datasift-Id']

                if of == 'gzip':
                        f = open("/tmp/DataSift-%s-%s.gz" % (str(self.request.headers['X-Datasift-Id']) , ts), 'w')
                else:
                        f = open("/tmp/DataSift-%s-%s.json" % (str(self.request.headers['X-Datasift-Id']) , ts), 'w')

                f.write(str(self.request.body))
                f.close

        self.set_status(200)
        self.write('{"success": true}')
        self.finish()

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8787)
    tornado.ioloop.IOLoop.instance().start()
