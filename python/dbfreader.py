#-*- coding:utf-8 -*-
"""
read forxpro dbf & FPT file
Author fan.fei@datatom.com
"""
import struct
import os
import sys
from collections import namedtuple


DBFHeader = namedtuple("DBFHeader", ['type','yy','mm','dd','recordnum','headersize','recordlen', 'tableflag'])
DBFField = namedtuple("DBFField", ['name','type','len','precision'])
MEMOHeader = namedtuple("MEMOHeader",['blocksize'])

class DbfReader:
    """
    Usage:
        db = DbfReader()
        db.open('dbffile.dbf')
        print db.cols
        for record in db.records:
            print db.val(db.cols[0], record)
        db.close()

    """
    def __init__(self, convertgbk= True):
        """
        set convertdb2312 = True will change charactor encoding from gb2312 to utf-8
        otherwise will leave as origin encoding
        default is True
        """
        self.fdb = None
        self.dbdata = None
        self.fmemo = None
        self.fields = None
        self.fields_pattern = ''
        self.header = None
        self.memo_data = None
        self.memo_header = None
        self.memo_block_size = 0
        self.memo_header_len = 0
        self.dbfrecords = None
        self.convertgb = convertgbk

    def open(self, db_name):
        """
        open a dbf table, load data into memory
        """
        filesize = os.path.getsize(db_name)
        if filesize <= 68:
            raise IOError, 'The file is not large enough to be a dbf file'

        memo_file = ''
        if os.path.isfile(db_name[0:-1] + 't'):
            memo_file = db_name[0:-1] + 't'
        elif os.path.isfile(db_name[0:-3] + 'fpt'):
            memo_file = db_name[0:-3] + 'fpt'
        elif os.path.isfile(db_name[0:-3] + 'FPT'):
            memo_file = db_name[0:-3] + 'FPT'

        if memo_file:
            self.fmemo = open(memo_file, 'rb')
            self.memo_size = os.path.getsize(memo_file)
            self.memo_data = self.fmemo.read()
            self.readmemohead()

        self.fdb = open(db_name, 'rb')
        self.dbdata = self.fdb.read()
        self.header = self.readdbfhead()
        self.readfields()

    def close(self):
        if self.fdb:
            self.fdb.close()
        if self.fmemo:
            self.fmemo.close()
        self.fdb = None
        self.dbdata = None
        self.fmemo = None
        self.fields = None
        self.fields_pattern = ''
        self.header = None
        self.memo_data = None
        self.memo_header = None
        self.memo_block_size = 0
        self.memo_header_len = 0
        self.dbfrecords = None

    def readdbfhead(self):
        #data = self.fdb.read(32)
        data = self.dbdata[0:32]
        header = DBFHeader(*struct.unpack('<B 3B L 2H 16x B 3x', data))
        return header

    def readfields(self):
        def _makefield(raw):
            tmp = struct.unpack('<11s c 4x B B 14x', raw)
            if self.convertgb:
                t = (tmp[0].strip('\0').decode('gbk').encode('utf-8'),) + tmp[1:]
            else:
                t = (tmp[0].strip('\0'),) + tmp[1:]
            return DBFField(*t)

        if not self.header:
            return
        #self.fdb.seek(32) #begin of fields
        #data = self.fdb.read(self.header.headersize - 32 - 1)
        b = buffer(self.dbdata, 32)
        data = b[:self.header.headersize - 32 - 1]
        self.fields = [_makefield(data[x:x+32]) for x in range(0, len(data), 32)]
        self.fields_pattern = '>x' + ''.join(map(lambda x:'%ds'%x.len, self.fields))
        #print self.fields_pattern


    def readmemohead(self):
        #self.fmemo.seek(0)
        #data = self.fmemo.read(8)
        data = self.memo_data[0:8]
        self.memo_header = MEMOHeader(*struct.unpack(">6x1H", data))
        size = self.memo_header.blocksize
        if not size:
            size = 512
        self.memo_block_size = size
        self.memo_header_len = size
        #print "memo block size: ", size

    def _readmemorecord(self, num, len = -1):
        if len <= 0:
            len = self.memo_block_size
        #self.fmemo.seek(offset)
        #return self.fmemo.read(len)
        offset = self.memo_header_len + num * self.memo_block_size
        data = buffer(self.memo_data, offset)
        return data[:len]


    def readmemo(self, num):
        result = ''
        buffer = self._readmemorecord(num)
        if len(buffer) <=0:
            return ''
        length = struct.unpack('>L', buffer[4:8])[0]
        if length <= self.memo_block_size - 8:
            return buffer[8:]
        restlen = length + 8 - self.memo_block_size
        restdata = self._readmemorecord(num + 1, restlen)
        if len(restdata) == 0:
            return ''
        return buffer[8:] + restdata

    def getmemodata(self, record):
        if self.fmemo:
            index = 0
            for field in self.fields:
                if field.type in 'MGBP' and record[index].strip():
                    #print "field type:", field.type
                    #print "len:",len(record[index])," value: ",record[index]
                    num = int(record[index].strip())
                    #print "num is: ", num
                    if num:
                        record[index] = self.readmemo(num -1).strip('\0')
                        #print "memo data ", self.fields[index].name, " ", record[index].decode('gb2312').encode('utf-8')
                index +=1

    def readrecord(self,n):
        #calc offset
        offset = self.header.headersize + n* self.header.recordlen
        #self.fdb.seek(offset)
        #rawdata = self.fdb.read(self.header.recordlen)
        b = buffer(self.dbdata, offset)
        rawdata = b[:self.header.recordlen]
        data = list(struct.unpack(self.fields_pattern, rawdata))

        self.getmemodata(data)
        if self.convertgb:
            return tuple([x.strip().decode('gbk').encode('utf-8') \
                    for x in data])
        else:
            return tuple([x.strip() for x in data])

    def val(self, colname, record):
        return record[self.cols.index(colname)]

    @property
    def cols(self):
        """
        cols() -> []
        get column name
        """
        return [field.name for field in self.fields]

    
    @property
    def records(self):
        """
        records() -> [(,),]
        return table's record in list of tuples
        """
        if not self.dbfrecords:
            self.dbfrecords = [self.readrecord(n) \
            for n in range(0, self.header.recordnum)]
        return self.dbfrecords

def printrecord(x):
    print '\t'.join(x)


if __name__ == '__main__':
    db = DbfReader()
    db.open(sys.argv[1])
    print db.cols
    for r in db.records:
        printrecord(r)
    db.close()
