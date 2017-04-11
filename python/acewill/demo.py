#!/usr/bin/python 
# coding: utf-8
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line
from tornado import web


import psycopg2
import momoko
import query
import json

DEFAULTDB = "chain_edinner_2016"

def usingdb(dbname):
    def dec(obj):
        obj.dbname = dbname
        return obj
    return dec


class BaseHandler(web.RequestHandler):
    class __metaclass__(type):
        def __new__(cls, name, bases, attr):
            for obj in attr.values():
                if hasattr(obj, 'dbname'):
                    attr['_dbname'] = getattr(obj, 'dbname')
                    print attr
                    break
            return type.__new__(cls, name, bases, attr)

    @property
    def db(self):
        try:
            return self.application.dbpool[self.dbname]
        except KeyError:
            return self.application.dbpool[DEFAULTDB]

    @property
    def dbname(self):
        return self._dbname

    def setdb(self, dbname):
        assert(databases.has_key(dbname))
        self._dbname = dbname




class TutorialHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def get(self):
        print self.dbname
        cursor = yield self.db.execute("select hisptid from c_pay_type_history;")
        print self.request.arguments
        self.write("Result: %s" % str(cursor.fetchone()))
        self.finish()

    def post(self):
        print self.request.arguments
        self.finish()


class YyeHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.REVENUE % param)
        yye = cursor.fetchone()[0] or 0.0
        
        self.write(json.dumps({"yye":float(yye)}))
        self.finish()


class KllHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.CUSTOMERS % param)
        kll = cursor.fetchone()[0]
        self.write(json.dumps({"kll":int(kll)}))
        self.finish()

class PayHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.PAY_ANALYZE % param)
        result = {}
        u = cursor.fetchone()
        result['paytype']= u[0]
        result['amountrate']= float(u[1])
        result['pricerate']= float(u[2])
        self.write(json.dumps(result))
        self.finish()


class PeriodHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.PERIOD_ANALYZE% param)
        result = {}
        u = cursor.fetchone()
        result['checkouttime']= u[0]
        result['yye']= float(u[1])
        result['ac']= float(u[2])
        result['tc']= u[3]
        self.write(json.dumps(result))
        self.finish()


class TableHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.TABLE_ANALYZE % param)
        result = {}
        u = cursor.fetchone()
        result['ftl']= float(u[0])
        self.write(json.dumps(result))
        self.finish()


class DiscountHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.DISCOUNT_ANALYZE % param)
        u = cursor.fetchone()
        result = {}
        result['total'] = float(u[0])
        result['rate'] = float(u[1])
        result['cost'] = float(u[2])
        self.write(json.dumps(result))
        self.finish()




class PopularHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.POPULAR_ANALYZE % param)
        u = cursor.fetchone()
        result = {}
        result['dish'] = u[0]
        result['count'] = u[1]
        self.write(json.dumps(result))
        self.finish()


class AbnormalHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        u = cursor.fetchone()
        result = {}
        result['ordertype'] = u[0]
        result['amount'] = u[1]
        self.write(json.dumps(result))
        self.finish()


class CookwaitHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        u = cursor.fetchone()
        result = {}
        result['shopname'] = u[0]
        result['dish'] = u[1]
        result['date'] = u[2]
        self.write(json.dumps(result))
        self.finish()


class AttendanceHandler(BaseHandler):
    @gen.coroutine
    @usingdb('chain_edinner_2016')
    def post(self):
        param = {'date':self.get_argument('date', default = '2016-01-01')}
        cursor = yield self.db.execute(query.ATTANDANCE_ANALYZE)
        u = cursor.fetchone()
        result = {}
        result['shopname'] = u[0]
        result['rate'] = float(u[1])
        self.write(json.dumps(result))
        self.finish()




def make_app():
    app = web.Application([
        (r'/', TutorialHandler),
        (r'/kll', KllHandler),
        (r'/period', PeriodHandler),
        (r'/pay', PayHandler),
        (r'/table', TableHandler),
        (r'/discount', DiscountHandler),
        (r'/popular', PopularHandler),
        (r'/cookwait', CookwaitHandler),
        (r'/abnormal', AbnormalHandler),
        (r'/attendance', AttendanceHandler),
        (r'/yye', YyeHandler)], 
        debug = True)
    return app




databases = {
        'edinner_3':'dbname=edinner_3 user=postgres password=postgres host=192.168.1.189 port=14103',
        'chain': 'dbname=chain user=postgres password=postgres host=192.168.1.189 port=14103',
        'chain_dinner_2016': 'dbname=chain_edinner_2016 user=postgres password=postgres host=192.168.1.189 port=14103'
        }



if __name__ == '__main__':
    parse_command_line()
    app = make_app()
    ioloop = IOLoop.instance()
    app.db = momoko.Pool(
            dsn = 'dbname=chain user=postgres password=postgres host=192.168.1.189 port=14103',
            size = 1,
            ioloop = ioloop,
            )

    app.dbpool = {}
    for db, connstr in databases.items():
        app.dbpool[db] = momoko.Pool(dsn = connstr, size = 1, ioloop = ioloop)

    for conn in app.dbpool.itervalues():
        future = conn.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        future.result()

    http_server = HTTPServer(app)
    http_server.listen(8888, '0.0.0.0')
    ioloop.start()
