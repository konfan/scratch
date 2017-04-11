# coding: utf-8
TEST = "select count(*) from c_user"

REVENUE = "select sum(cost) as yye from o_order_history where orderstatus=3 and \
        (checkouttime::timestamp)::date=('2016-02-14 19:05'::timestamp)::date"

CUSTOMERS = "select count(tid) as kll from o_order_history where orderstatus=3 and \
        (checkouttime::timestamp)::date=('2016-02-14 19:05'::timestamp)::date"


PAY_ANALYZE = "select paytype_,round(c.amounta::numeric/c.amountb::numeric,4) amountrate, pricerate from (select paytype paytype_,a.amounta,b.amountb, round(a.pricea/b.priceb,4) as pricerate from \
        (select a.paytype,count(c.cost) as amounta, sum(c.cost) as pricea \
        from c_pay_type a, c_pay_history b, o_order_history c \
        where b.ptid=a.ptid and b.oid=c.oid and (c.checkouttime::timestamp)::date = ('%(date)s'::timestamp)::date \
        group by a.paytype order by count(c.cost) desc ) a, \
        (select  count(c.cost) as amountb, sum(c.cost) as priceb \
        from c_pay_type a, c_pay_history b, o_order_history c \
        where b.ptid=a.ptid and b.oid=c.oid and (c.checkouttime::timestamp)::date = ('%(date)s'::timestamp)::date ) b) c"


PERIOD_ANALYZE = "SELECT * FROM ( SELECT to_char((checkouttime::timestamp), 'yyyy-mm-dd HH24:')||(case when to_char((checkouttime::timestamp), 'MI')<'30' then '00' else '30' end) as checkouttime, sum(cost) as YYE,round(AVG(cost),2) as AC, COUNT(cost) as TC \
        FROM o_order_history WHERE orderstatus=3 AND (checkouttime::timestamp)::date = ('%(date)s'::timestamp)::date GROUP BY to_char((checkouttime::timestamp), 'yyyy-mm-dd HH24:')||(case when to_char((checkouttime::timestamp), 'MI')<'30' then '00' else '30' end) ) A ORDER BY checkouttime"


TABLE_ANALYZE = "select round((count(b.tid)-a.sumtable)/a.sumtable,1) ftl  \
        from sls_shop a, o_order_history b \
        where b.orderstatus=3 and a.sid=b.slsid and \
        (checkouttime::timestamp)::date=('%(date)s'::timestamp)::date"


DISCOUNT_ANALYZE = "select sum(total) total, rate, sum(cost) costt from o_order_history \
        where rate<1 and (checkouttime::timestamp)::date = ('%(date)s'::timestamp)::date group by rate"


POPULAR_ANALYZE = "select dish,count(dish) redu from o_dish a, o_order_item_history b \
        where a.status=1 and a.id=b.did and itemstatus=2 and \
        (checkouttime::timestamp)::date=('%(date)s'::timestamp)::date \
        group by a.dish order by count(dish) order by count(dish) desc limit 10"


ABNORMAL_ANALYZE = "SELECT '退单' ORDER_TYPE, COUNT(totaldish) ShuLiang FROM o_order_history A \
        WHERE orderstatus=4 AND  (A.checkouttime::timestamp)::date = ('2016-01-14 19:05'::timestamp)::date \
        UNION ALL \
        SELECT '退菜' ORDER_TYPE, COUNT(PRICE) ShuLiang FROM o_order_item_history A WHERE itemstatus=3 AND (ORDERTIME::timestamp)::date = ('2016-01-14 19:05'::timestamp)::date"


COOK_WAIT = "SELECT C.shopname,D.dish,date_part('MIN', A.newtime::timestamp - B.ordertime::timestamp) qicai_time \
        FROM o_order_history A, o_order_item_history B,sls_shop C, o_dish D \
        WHERE orderstatus=3 AND A.tid IS NOT NULL AND A.OID=B.OID AND A.sid=C.sid AND B.did=D.did AND (checkouttime::timestamp)::date = ('2016-01-14 19:05'::timestamp)::date \
        AND date_part('MIN', A.newtime::timestamp - B.ordertime::timestamp)>20"


ATTANDANCE_ANALYZE = "SELECT A.shopname,ROUND(SUM(B.people::numeric)/A.seat::numeric,2) SZL FROM sls_shop A, o_order_history B \
        WHERE A.sid=B.slsid AND A.SEAT>0 AND B.outorderid IS NULL AND (checkouttime::timestamp)::date = ('2016-02-14 19:05'::timestamp)::date GROUP BY A.shopname,A.SEAT"

