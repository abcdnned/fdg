#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join

#runtime parameters
JAVA_MAP_NAME='JxbCoreMapFlds'
PKGNAME='individual.jxb'
DEF_START_SURFIX_NUM=7
DEF_PREFIX='Core'
INPUT_PATH='/home/tom/dcdreq/jx_core/p.txt'
LIMIT=55
OUTPUT_PATH='/home/tom/dcdreq/jx_core/'
MAP_CONS_NAME='FIELD_MAP'

#custome implements method
def hasdefname(line):
    return '接口总长度' in line or '接口)' in line

def end(line):
    return '场景及案例' in line

def checkfield(line):
    if mode == 0:
        return mode0field(line)
    elif mode == 1:
        return mode1field(line)

def mode1field(line):
    return line == 'A\n' or line == 'I\n' or line == 'D\n'

def mode0field(line):
    r = 'Char' in line or 'Int' in line or 'decimal' in line or 'Decimal' in line or 'INTEGER' in line or 'SmallInt' in line or 'Int' in line
    return r and len(line) < 10

def getname(line):
    if mode == 0 :
        return line[:line.find('(')]
    elif mode == 1:
        return line[:line.find('接口总长度')]

def getMode(line):
    if '接口总长度' in line :
        return 1
    elif '接口)' in line :
        return 0
    return -1

def getlength(ln, lines):
    if mode == 0:
        return lines[ln+2][:-1].split(',')[0]
    elif mode == 1:
        return lines[ln+2][:-1].split(',')[0]

def avaiableName(s):
    for c in s:
        if not (c in '_1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            return False
    return True

def getfn(ln, lines):
    if mode == 0:
        i = ln + 5
        while not(avaiableName(lines[i].strip())):
            i += 1
        return lines[i].strip()
    elif mode == 1:
        i = ln - 1
        while not(avaiableName(lines[i].strip())):
            i += 1
        return lines[i].strip()

#system method
def getin(content,start,end):
    s=content.find(start)
    e=content.find(end,s+len(start))
    return content[s+len(start):e]

def getnumin(content):
    return ''.join(c for c in content if c.isdigit())

def deffldmap(mapn):
    return 'static final Map<String,DecodeField[]> {} =new HashMap<String,DecodeField[]>();\n'.format(mapn)

def putfld(mapn,key,consn,fldn):
    return '{}.put("{}",{}.{});\n'.format(mapn,key,consn,fldn)

def fielddefine(index,l,fn,record=True,charset='Encoding.CHARSET'):
    if not record:
        return '{{ {{ {}, null, {}, {} }}, {{ "", null, false, "{}" }} }},\n'.format(index,l,charset,fn)
    return '{{ {{ {}, null, {}, {} }}, {{ "", ValueType.STRING, false, "{}" }} }},\n'.format(index,l,charset,fn)

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

def gendeffilehead(pkg,deffn):
    return 'package cn.com.netis.dcd.parser.decoder.bank.{};\nimport cn.com.netis.dcd.parser.huygens.field.DecodeField;\nimport cn.com.netis.dcd.parser.huygens.field.Encoding;\nimport cn.com.netis.dcd.parser.huygens.field.bank.BankFieldFactory;\nimport cn.com.netis.dp.commons.lang.ValueType;\n\npublic class {} {{\n\n'.format(pkg,deffn)


def genmaphead(pkg,classn):
    return 'package cn.com.netis.dcd.parser.decoder.bank.{};\n\nimport java.util.HashMap;\nimport java.util.Map;\n\nimport cn.com.netis.dcd.parser.huygens.field.DecodeField;\n\npublic class {} {{\n'.format(pkg,classn)

def writedefs(defs,fld,build,f):
    o=open(f,'w')
    o.write(gendeffilehead(PKGNAME,deffn+name))
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
    o.write(genmaphead(PKGNAME,JAVA_MAP_NAME))
    o.write(mapdef)
    o.write('static {\n')
    o.write(regs)
    o.write('}\n')
    o.write('}\n')
    o.flush()
    o.close()

i=open(INPUT_PATH)
lines=i.readlines()

rraflag=0

defs=''
fld=''
build=''
regs=''

deffn=DEF_PREFIX

firstflag=True
index=0
name=''

defined=0
limit=LIMIT
n=DEF_START_SURFIX_NUM
mode = -1



outputws=OUTPUT_PATH

for ln,line in enumerate(lines):
    if end(line):
        break
    if hasdefname(line):
        if firstflag:
            firstflag=False
        else:
            defs+=definecloser()
            writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,name))
            defs=''
            fld=''
            build=''
            defined=0
            n+=1
        index=0
        mode = getMode(line)
        name=getname(line)
        #figure out name of defines, fields and build statement
        defname='DEF_'+name.upper()
        fieldname='FIELD_'+name.upper()
        defs+=definehead(defname)
        fld+=staticfield(fieldname,defname)
        build+=fieldbuild(fieldname,defname)
        regs+=putfld(MAP_CONS_NAME,name,'{}{}'.format(deffn,name),fieldname)
        defined+=1
    if checkfield(line):
        #figure out what's the name of field and the length of this field
        fn = getfn(ln ,lines)
        length = getlength(ln ,lines)
        print '{} {}'.format(fn,length)
        defs+=fielddefine(index,length,fn)
        index+=1

if defined>0:
    defs+=definecloser()
    writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,name))

i.close()

writereg(n,regs,'{}{}.java'.format(outputws,JAVA_MAP_NAME),deffldmap(MAP_CONS_NAME))


