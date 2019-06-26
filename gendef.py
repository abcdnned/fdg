#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join

#runtime parameters
JAVA_MAP_NAME='WebbankBodyFlds'
PKGNAME='jyrcb'
DEF_START_SURFIX_NUM=7
DEF_PREFIX='WebbankFldDef'
INPUT_PATH='jyrcbinner.csv'
LIMIT=55
OUTPUT_PATH='c:/Users/tom.yang/Desktop/jyrcbinner/'
MAP_CONS_NAME='FIELD_MAP'
FLD_LEN_IDX=2
FLD_NAME_IDX=0

#custome implements method
def hasdefname(line):
    return 'zfpt' in line

def checkdefine(line):
    return line[:4]=='1219'

def checkfield(line):
    return line[0].isalpha()

def getname(line):
    s=line.find('zfpt')
    return line[s:s+8]

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



outputws=OUTPUT_PATH

for ln,line in enumerate(lines):
    if hasdefname(line):
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
            #figure out name of defines, fields and build statement
            rra='REQ_' if rraflag==0 else 'RESP_'
            rraflag=(rraflag+1)%2
            defname='DEF_'+rra+name
            fieldname='FIELD_'+rra+name
            defs+=definehead(defname)
            fld+=staticfield(fieldname,defname)
            build+=fieldbuild(fieldname,defname)
            regs+=putfld(MAP_CONS_NAME,name+rra[:-1].lower(),'{}{}'.format(deffn,n),fieldname)
            defined+=1
        if checkfield(line):
            #figure out what's the name of field and the length of this field
            its=line.split(',')
            fn=its[FLD_NAME_IDX]
            length=getnumin(its[FLD_LEN_IDX])
            defs+=fielddefine(index,length,fn)
            index+=1

if defined>0:
    defs+=definecloser()
    writedefs(defs,fld,build,'{}{}{}.java'.format(outputws,deffn,n))

i.close()

writereg(n,regs,'{}{}.java'.format(outputws,JAVA_MAP_NAME),deffldmap(MAP_CONS_NAME))


