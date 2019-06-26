#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os.path import join

#runtime parameters
JAVA_MAP_NAME='WebbankBodyFlds'
PKGNAME='individual.hnrcu'
DEF_START_SURFIX_NUM=sys.argv[1][0:4]
DEF_PREFIX='CoreSopDef'
INPUT_PATH='/home/tom/dcdreq/hnrcu_coresop/810/protocol/{}'.format(sys.argv[1])
LIMIT=55
OUTPUT_PATH='/home/tom/dcdreq/hnrcu_coresop/810/protocol/'
MAP_CONS_NAME='transIntfMap'
FLD_LEN_IDX=2
FLD_NAME_IDX=0

#custome implements method
def getmapname(rra):
    if rra[0] == 'R':
        return 'reqDataMap'
    else:
        return MAP_CONS_NAME

def checkdefine(line):
    return 'OBJ' in line

def getrra(line):
    if 'I W' in line:
        return 'RQ_' + line[14:18]
    else:
        return 'TF_' + line[13:19]

def checkfield(line):
    return 'FLD:' in line

def getfieldname(line):
    s = line.find('FLD:')
    s = s + 5
    return line[s:s+6]

def getregistername(rra):
    return rra[3:]

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
    o.write(gendeffilehead(PKGNAME,deffn+str(n)))
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

deffn=DEF_PREFIX

defineIndex=0
index=0
name=''

defined=0
limit=LIMIT
n=DEF_START_SURFIX_NUM


outputws=OUTPUT_PATH

for ln,line in enumerate(lines):
    if checkdefine(line):
        if defineIndex>0 and defineIndex < 2:
            defs+=definecloser()
        if defineIndex>1:
            break;
        else:
            defineIndex+=1
        if defined>=limit:
            writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,n))
            defs=''
            fld=''
            build=''
            defined=0
            n+=1
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
        regs+=putfld(mn,rn,'{}{}'.format(deffn,n),fieldname)
        defined+=1
    if checkfield(line):
        #figure out what's the name of field and the length of this field
        fn = getfieldname(line);
        defs+=fielddefine(index,1,fn)
        index+=1

if defined>0:
    defs+=definecloser()
    writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,n))

i.close()

writereg(n,regs,'{}{}.java'.format(outputws,JAVA_MAP_NAME),deffldmap(MAP_CONS_NAME))


