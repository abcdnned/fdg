#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join
import os

def getin(content,start,end):
    s=content.find(start)
    e=content.find(end,s+len(start))
    return content[s+len(start):e]

def getnumin(content):
    return ''.join(c for c in content if c.isdigit())

def getValidCharIn(content,validchars):
    return ''.join(c for c in content if validchars.find(c)>0)


def hasdefname(ln,line):
    return ln==2

def checkdefine(line):
    return line.split(',')[0]=='2'

def checkfield(line):
    its=line.split(',')
    return its[0].isdigit() and not its[2]=='TRXTYPE'

def deffldmap(mapn):
    return 'static final Map<String,DecodeField[]> {} =new HashMap<String,DecodeField[]>();\n'.format(mapn)

def putfld(mapn,key,consn,fldn):
    return '{}.put("{}",{}.{});\n'.format(mapn,key,consn,fldn)

def fielddefine(index,l,fn,record=True,charset='Encoding.CHARSET',cache=False):
    needcache='true' if cache else 'false'
    if not record:
        return '{{ {{ {}, null, {}, {} }}, {{ "", null, {}, "{}" }} }},\n'.format(index,l,charset,needcache,fn)
    return '{{ {{ {}, null, {}, {} }}, {{ "", ValueType.STRING, {}, "{}" }} }},\n'.format(index,l,charset,needcache,fn)

def definehead(name):
    return ' private static final Object[][][] {} = {{ \n'.format(name)

def definecloser():
    return '};\n'

def staticfield(fieldname,defname):
    return 'static final DecodeField[] {} = new DecodeField[{}.length];\n'.format(fieldname,defname)

def fieldbuild(fieldname,defname):
    return 'BankFieldFactory.buildFields({},{});\n'.format(fieldname,defname)

def defineregmap(mapname,regname,fieldname):
    return '{}.put("{}", {})\n'.format(mapname,regname,fieldname)

def searchline(lines,s,pattern,limit):
    for i in range(limit):
        if pattern in lines[s+i]:
            return s+i
    return -1

def getname(line):
    return line.split(',')[2]

def gendeffilehead(pkg,deffn):
    return 'package cn.com.netis.dcd.parser.decoder.bank.{};\nimport cn.com.netis.dcd.parser.huygens.field.DecodeField;\nimport cn.com.netis.dcd.parser.huygens.field.Encoding;\nimport cn.com.netis.dcd.parser.huygens.field.bank.BankFieldFactory;\nimport cn.com.netis.dp.commons.lang.ValueType;\n\npublic class {} {{\n\n'.format(pkg,deffn)


def genmaphead(pkg,classn):
    return 'package cn.com.netis.dcd.parser.decoder.bank.{};\n\nimport java.util.HashMap;\nimport java.util.Map;\n\nimport cn.com.netis.dcd.parser.huygens.field.DecodeField;\n\npublic class {} {{\n'.format(pkg,classn)

def writedefs(defs,fld,build,f):
    print f
    o=open(f,'w')
    o.write(gendeffilehead('jyrcb',deffn+str(n)))
    o.write(defs)
    o.write(fld)
    o.write('static {\n')
    o.write(build)
    o.write('}\n')
    o.write('}\n')
    o.flush()
    o.close()

def writereg(n,regs,f,mapdef):
    o=open(f,'w')
    o.write(genmaphead('jyrcb','BillFldMap'))
    o.write(mapdef)
    o.write('static {\n')
    o.write(regs)
    o.write('}\n')
    o.write('}\n')
    o.flush()
    o.close()

ws='c:/Users/tom.yang/Desktop/jyrcbbill/'

rraflag=0

defs=''
fld=''
build=''
regs=''

deffn='BillFldDef'

firstflag=True
index=0
name=''

defined=0
limit=20
n=1

validchars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890'

outputws=ws
mapdefn='BillFldMap'

for parent,dirs,files in os.walk(ws):
    for f in files:
        if f[:4].isdigit():
            i=open(join(ws,f))
            lines=i.readlines()
            for ln,line in enumerate(lines):
                if hasdefname(ln,line):
                    name=getname(line)
                    rraflag=0
                else:
                    if checkdefine(line):
                        if firstflag:
                            firstflag=False
                        else:
                            defs+=definecloser()
                        if defined>=limit:
                            writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,n))
                            defs=''
                            fld=''
                            build=''
                            defined=0
                            n+=1
                        index=0
                        rra='REQ_' if rraflag==0 else 'RESP_'
                        rraflag=(rraflag+1)%2
                        defname='DEF_'+rra+name
                        fieldname='FIELD_'+rra+name
                        defs+=definehead(defname)
                        fld+=staticfield(fieldname,defname)
                        build+=fieldbuild(fieldname,defname)
                        regs+=putfld('FIELD_MAP',name+rra[:-1].lower(),'{}{}'.format(deffn,n),fieldname)
                        defined+=1
                    if checkfield(line):
                        its=line.split(',')
                        fn=getValidCharIn(its[2],validchars)
                        length=its[4]
                        if len(fn)==0:
                            fn=name+'F'+str(index)
                        length=getnumin(length)
                        defs+=fielddefine(index,length,fn)
                        index+=1
            i.close()
            rraflag=0
            writereg(n,regs,'{}{}.java'.format(outputws,mapdefn),deffldmap('FIELD_MAP'))

    if defined>0:
        defs+=definecloser()
        writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,n))
        defs=''
        fld=''
        build=''
        defined=0
        n+=1



