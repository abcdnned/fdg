from os.path import join
import os.path
import os

wspath='c:\\pyws'


with open(join(wspath,'fielddefine')) as f:
    result=[]
    index=0
    lines=f.readlines()
    for line in lines:
        index+=1
        len_start=0
        for i,c in enumerate(line):
            if c>='0' and c<='9':
                len_start=i
        name=line[:len_start]
        length=line[len_start:]
        result.append('{{{{{}, null,{} , Encoding.CHARSET}}, {{"{}", ValueType.STRING, false, "{}"}}}},\n'.format(str(index),length,name,name))
    wf=open(join(wspath,'fielddefine.java'),'w')
    wf.writelines(result)
    wf.flush()
    wf.close()
