import pandas as pd
import time
#导入time库，时间处理，时间格式化，计时
from tqdm import tqdm
#tqdm进度条显示
import os
#导入os模块，os模块提供各种 Python 程序与操作系统进行交互的接口
import json
#JSON是用于存储和交换数据的语法。
\
def operate1(data):
    #定义一个名为operate1的函数，其参数为data
    '''
    筛选留下“FCU送VCU心跳”连续变化
    （连续变化是指相邻60行内有变化，若大于60行无变化，
    则只保留第1行数据）的数据
    '''
    data['diff'] = data["FCU送VCU心跳"].diff()
    starttime = time.time()
    for i in range(len(data)):
        #给i赋值
        data_i = data.iloc[i:i+60,:]
        #先行后列，行取60行，列取全部
        if len(data_i) == 0:
            print('break1')
            break
        if data_i["FCU送VCU心跳"].nunique()==1:
            #如果返回每列的唯一值的数量唯一，说明60行内无变化，diff为0，因此只取第一行
            data_i_ = data.iloc[i+1:, :]
            #表示无变化的60行中第一行的索引
            data_i_same = data_i_[data_i_['diff'].map(lambda x:x!=0)]
            #匿名函数lambda筛选x不为0
            if len(data_i_same) == 0:
                data.drop(data.index[i+1:],inplace=True)
                #drop函数，删除以index
                # index() 函数用于从列表中找出某个值第一个匹配项的索引位置。
                # inplace = True：不创建新的对象，直接对原始对象进行修改
                print('break2')
                break
            data_i_index_end = data_i_same.index[0]
            data.drop(index = range(data_i_.index[0], data_i_index_end),inplace=True)
    endtime = time.time()
    print('operate1-运行的时间为:{}secs'.format(round(endtime - starttime, 2)))
    #打印运行时间
    return data

def operate2(data):
    '''
    在上一步基础上，
    筛选留下“最高警告等级”为1或0的数据
    
     '''
    data = data.loc[(data['最高警告等级']==1) | (data['最高警告等级']==0),:]
    #筛选并取并集
    return data 

def operate3(data):
    '''
    在上一步基础上，
    筛选留下“电气路设定1（自变量）”为192的数据
    '''
    data = data.loc[data['电气路设定1（自变量）']==192]
    return data 

def operate4(data,length):
    """
    在上一步基础上，
    筛选留下连续（连续是指该组数据内没有任何一行被筛除）大于600行的数据为一组
    """
    group_list = []
    index_list = data.index
    block_list = []
    for x in index_list:
        block_list.append(x)
        if x+1 not in index_list:
            if len(block_list)>length:
                group_list.append(data.loc[block_list[0]:block_list[-1]+1,:])
            block_list = []
    return group_list

def operate5(data):
    '''
    在上一步基础上，筛选留下同时满足
    74.5<“冷却路反馈3”<77.5与74.5<“冷却路反馈5”<77.5的数据
    '''
    block_list = []
    for block in data:
        block1 = block[((74.5<block['冷却路反馈3']) & (block['冷却路反馈3']<77.5)) 
                       & 
                       ((74.5<block['冷却路反馈5']) & (block['冷却路反馈5']<77.5)) 
                      ]
        block_list.append(block1)
    return block_list

def operate6(data):
    '''
    在上一步基础上，
    筛除每组数据的前180行数据
    '''
    block_list = []
    for block in data:
        block1 = block.drop(block.index[0:180])
        block_list.append(block1)
    return block_list

def operate7(data):
    '''
    在上一步基础上，
    将每组数据按照式（1）进行计算，
    求取“电堆性能值”。
    '''
    block_list = []
    for block in data:
        m = block['系统性能均值'].mean()
        block_list.append({
            'data':block,
            'v_mean':m
        })
    return block_list

def data_create(path, filepackage_list):
    """_summary_

    Args:
        path (str): Mxx系统文件夹所在路径
        filepackage_list (list): 系统名列表

    Returns:
        dict: 包含多个系统的每组稳态数据以及每组的【系统性能均值】
    """
    dict1 = {}
    for package in tqdm(filepackage_list):
        print(f'系统 {package} 运行')
        dict1[package] = []
        sys_list = []
        for file in os.listdir(os.path.join(path,package)):
            if file == '.DS3ww_Store':
                continue
            print(f'读取文件：{os.path.join(os.path.join(path,package,file))}')
            current_file = os.path.join(os.path.join(path,package,file))
            data = pd.read_csv(current_file)
            sys_list.append(data)
        data = pd.concat(sys_list)        
        data.index = range(len(data))
        # return data
        data_ = data
        data_operate1 = operate1(data_)
        data_operate2 = operate2(data_operate1)
        data_operate3 = operate3(data_operate2)
        group_list = operate4(data_operate3,600)
        data_operate5 = operate5(group_list)
        data_operate6 = operate6(data_operate5)
        data_operate7 = operate7(data_operate6)
        for block in data_operate7:
            if len(block['data'])>0:
                dict1[package].append(block)
    return dict1

if __name__ == "__main__":
    """调用示例"""
    """上述调用示例运行较为缓慢，选手可进行优化加速"""
    # path = './data/'
    # file_test = data_create(path, ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'])
    # file_test 为一字典，其中包含索要处理系统，keys：'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'
    # file_test['M1]为一列表，其中包含n组稳态过程的数据
    # file_test['M1][0]为一dict，表示M1系统第一组稳态，keys：'data', 'v_mean'。其中，data为对应数据，v_mean为该组系统性能均值。
    # 每组v_mean，对应给出的训练集答案
    path = 'example/'
    #下面的代码是选择有用的数值并计算出稳态均值
    file_test = data_create(path, ['M1'])
    if not os.path.exists('processed'):
        #创建了processed的文件
        os.makedirs('processed')

    for key in file_test.keys():
        #把所有结果记录
        for idx, states in enumerate(file_test[key]):

            data_frame, v_mean = states['data'], states['v_mean']
            data_json = json.loads(data_frame.to_json(orient='index'))
            data_json['v_mean'] = v_mean
            #形成json字符串

            with open(f'processed/{key}_{idx}.json', 'w', encoding='utf8') as fd:
                json.dump(data_json, fd, ensure_ascii=False)
                #把json写到文件里