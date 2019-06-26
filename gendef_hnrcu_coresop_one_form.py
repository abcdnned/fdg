#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os.path import join

#runtime parameters
JAVA_MAP_NAME='WebbankBodyFlds'
PKGNAME='individual.hnrcu'
DEF_START_SURFIX_NUM=1
DEF_PREFIX='CoreSopForm'
INPUT_PATH='/home/tom/tmp/gensop/6678.txt'
LIMIT=55
OUTPUT_PATH='/home/tom/tmp/gensop/2/'
MAP_CONS_NAME='formMap'
FLD_LEN_IDX=2
FLD_NAME_IDX=0

deffn=DEF_PREFIX
#custome implements method
def checktrans(line):
    return 'FRM:' in line

def getdefname(line):
    return DEF_PREFIX + line[21:27]

def getmapname(rra):
    return MAP_CONS_NAME

def checkdefine(line):
    return line[16:19] == 'FRM'

def getrra(line):
    return 'FORM_' + line[21:27]

def checkfield(line):
    return line[24:27] == 'FLD'

def getfrmname(line):
    return line[21:27]

def getfieldname(frmname, line):
    s = line.find('FLD:')
    s = s + 5
    return frmname + '_' + line[s:s+6]

def getregistername(rra):
    return rra[5:]

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
    return '{{ {{ {}, Encoding.BINARY, 1, Encoding.CHARSET }}, {{ "{}", ValueType.STRING, false, "{}" }} }},\n'.format(index,fn,fn)

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
    o.write(gendeffilehead(PKGNAME,deffn))
    o.write(defs)
    o.write(fld)
    o.write('static {\n')
    o.write(build)
    o.write('}\n')
    o.write('}\n')
    o.flush()
    o.close()

def writereg(n,regs,f,mapdef):
    o=open(f,'a')
    o.write(regs)
    o.flush()
    o.close()

i=open(INPUT_PATH)
lines=i.readlines()

rraflag=0

defs=''
fld=''
build=''
regs=''


defineIndex=0
index=0
name=''

defined=0
limit=LIMIT
n=DEF_START_SURFIX_NUM


outputws=OUTPUT_PATH

frmname=''

for ln,line in enumerate(lines):
    if checktrans(line):
        if defined > 0 and defineIndex > 0:
            defs+=definecloser()
            writedefs(defs,fld,build,'{}{}.java'.format(outputws,deffn))
            defs=''
            fld=''
            build=''
            deffn=getdefname(line)
        else:
            deffn=getdefname(line)
        defined+=1
        defineIndex = 0
    if checkdefine(line):
        frmname=getfrmname(line)
        if defineIndex == 1:
            defs+=definecloser()
        if defineIndex>1:
            defineIndex+=1
            continue
        else:
            defineIndex+=1
        index=0
        #figure out name of defines, fields and build statement
        rra=getrra(line);
        defname=rra+'_DEFS'
        fieldname=rra+'_FIELDS'
        defs+=definehead(defname)
        fld+=staticfield(fieldname,defname)
        build+=fieldbuild(fieldname,defname)
        rn = getregistername(rra)
        mn = getmapname(rra)
        regs+=putfld(mn,rn,'{}'.format(deffn),fieldname)
    if checkfield(line):
        if defineIndex>2:
            continue
        #figure out what's the name of field and the length of this field
        fn = getfieldname(frmname, line);
        defs+=fielddefine(index,1,fn)
        index+=1

if defined>0:
    defs+=definecloser()
    writedefs(defs,fld,build,'{}{}.java'.format(outputws,deffn))

i.close()

writereg(n,regs,'{}{}.java'.format(outputws,JAVA_MAP_NAME),deffldmap(MAP_CONS_NAME))


