import numpy as np
import ast
import re

# 数组转字符串
def array_to_string(array):
    ret=''
    i=0
    for s in array:
        if i>0:
            ret=ret+','
        ret=ret+str(s)
        i=i+1
    return ret

# 字符串转数组

# arr = [1,2,3,4,5,6]
# #求方差
# arr_var = np.var(arr)
# #求标准差
# arr_std = np.std(arr,ddof=1)
# print("方差为：%f" % arr_var)
# print("标准差为:%f" % arr_std)

def string_to_nparray(text):
    # 将,替换为空格
    text = text.replace(",", " ")
    # 去除换行
    text = text.replace('\n', '')
    text = re.sub('\[\s+', '[', text)
    text = re.sub('\s+]', ']', text)
    # 添加 ','
    xs = re.sub('\s+', ',', text)
    # 转换回numpy.array
    return np.array(ast.literal_eval(xs))


if __name__=='__main__':
    a= string_to_nparray('[  16.6206 16.8443 16.9422 16.9282 16.7814 16.3409 16.0193 15.8375 16.9213 16.6486 16.3619 16.1451 16.1941 16.25   17.194  16.6835 16.6556 16.1032 16.1171  ]')
    print(a)