from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json
import os



'''
设置停留时间
'''
def sleep_time():
    time.sleep(30)

'''
加载浏览器驱动

'''
def load_driver(url,browser,path):
    
    # Chrome驱动加载
    if browser == 'Chrome':
        driver = webdriver.Chrome(executable_path=path)
    # Edge驱动加载
    elif browser == 'Edge':
        driver = webdriver.Edge(executable_path=path)
    #driver.minimize_window()  # 最小化界面
    # 发起请求
    driver.get(url)
    return driver

'''
模拟登录
'''
def login(driver,username_xpath,password_xpath,button_xpath,username,password):
    username_field = driver.find_element_by_xpath(username_xpath)
    password_field = driver.find_element_by_xpath(password_xpath)
    # 输入用户名和密码
    username_field.send_keys(username)
    password_field.send_keys(password)
    # 提交form
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    #driver = switch(driver)
    time.sleep(5)
    #print(driver.current_url)
    check = driver.find_element_by_css_selector('p[class="mdMN06Number"]')
    print("验证码为：",format(check.text))
    time.sleep(15)
    return driver


'''
根据xpath跳转到对应界面
'''
def find_element(driver,xpath):
    element = driver.find_element_by_xpath(xpath)
    element.click()
    return driver


'''
更新driver
'''
def switch(driver):
    handlers = driver.window_handles
    driver.switch_to.window(handlers[-1])
    return driver


'''
关闭页面
'''
def quit(driver):
    driver.quit()


'''
模拟用户到达群聊界面
'''
def driver_chat(url,username,password,browser,driver_path):
    driver = load_driver(url,browser,driver_path)
    #link = '/html/body/div/div[1]/main/div/div/div[1]/div/div/div/div[2]/div[2]/div/a[1]'   #这是之前的xpath，但是后面官方修改了界面，变成了下面这个链接
    link = '/html/body/div/div[1]/div[1]/div[3]/div/div[2]/a'
    driver = find_element(driver,link)
    sleep_time()
    login1 = '/html/body/div[2]/div/div[3]/div/form/div/input'
    driver = find_element(driver,login1)
    sleep_time()
    username_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[1]/input'
    password_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[2]/input'
    button_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[3]/button'
    driver = login(driver,username_xpath,password_xpath,button_xpath,username,password)
    driver = switch(driver)
    message = '/html/body/div[1]/div/div/section/div/ul/li[2]/a/div'
    #message = '/html/body/div/div/div/aside/div/div/div/section/div[2]/div/ul/li/a'
    sleep_time()
    driver = find_element(driver,message)
    sleep_time()
    user = '/html/body/div/div/div/section/div/div/section/div/div[2]/a/a/article/section'
    driver = find_element(driver,user)
    sleep_time()
    account = '/html/body/div/div/div/section/div/div/section/div/div/section[1]/p/p/a'
    driver = find_element(driver,account)
    
    driver = switch(driver)
    sleep_time()
    
    chats = '/html/body/div/div[1]/nav/div/ul[1]/li[8]/a'
    driver = find_element(driver,chats)
    sleep_time()
    driver = switch(driver)
    '''/html/body/div[2]/div/div[1]/div/div[2]/nav/div[1]/a
    basic = '/html/body/div[2]/div/div[1]/div[1]/div[2]/nav/div[3]/div[2]/div[2]/a'
    driver = find_element(driver,basic)'''
    return driver

'''
获取每个群聊的url地址
'''
def get_group_url(driver,group):
    driver = find_element(driver,group)
    driver = switch(driver)
    url = driver.current_url
    sleep_time()
    return driver,url


'''
下载群聊文件
'''
def download(driver):
    download = '/html/body/div[2]/div/div[1]/div[1]/main/div/div[2]/section[4]/div[3]/div/button'
    driver = find_element(driver,download)
    sleep_time()

'''
从html中获取群聊对应的div
'''
def get_div(driver,url):
    driver.get(url)
    #html_content = driver.page_source
    sleep_time()
    div_list = driver.find_elements_by_css_selector('div[class="position-relative"]')
    return div_list

'''
创建群聊消息保存文件
'''
def create_file(path):
    file = open(path,'a',encoding='utf-8')
    return file


'''
用户类型判断
'''
def user_type(user_name):
    # 这里用户分为用户发送和机器人发送或自动回复
    if user_name == None or user_name.text.strip() == 'Auto-response':
        user_name = 'Auto-response'
        sender_type = 'Account'
    else:
        user_name = user_name.text.strip()
        sender_type = 'User'
    return user_name,sender_type


'''
日前转换
在页面上如果是今天或昨天发送的内容则转换为具体的时间，方便存储
'''
def date_switch(date):
    if str(date) == 'Today':
        date = datetime.now()
        date = date.strftime("%a, %b %d")
    if str(date) == 'Yesterday':
        date = datetime.now()-timedelta(days=1)
        date = date.strftime("%a, %b %d")
    return date

def get_text_img_voice(content_text_div,content_img,voices,filename):
    content_list = []
    # 获取具体的聊天记录
    if content_text_div != []:
        for content in content_text_div:
            content_list.append({'text':content.get_attribute('textContent').strip()})
            #print('content',format(content.get_attribute('class')))
    if content_img != []:
        for content in content_img:
            class_img = content.get_attribute('class')
            if class_img == 'chat-item-sticker' or class_img == 'sticon emojione':
                content_list.append({'image url':content.get_attribute('src')})
            else:
                img = []
                img.append({'image url':content.get_attribute('src')})
                img.append({'image path':filename})
                content_list.append(img)
    if voices != []:
        for voice in voices:
            content_list.append([{'voice path':filename},{'voice time':voice.text.strip()}])
            
    return content_list

def user_detail(user_detail_file,member_list,user_detial_id,user_all_list):
    for member in member_list:
        user_detail = {}
        user_detial_id = user_detial_id+1
        user_detail['user_name'] = member
        #user_all_list.append(member) 
        user_detail['auto_id'] = user_detial_id
        
        user_detail['group_type'] = 1
        user_detail['data_source'] = 'TRS'
        user_detail['update_time'] = str(datetime.now())
        user_detail['crawler_time'] = str(datetime.now())
        user_detail['intime'] = str(datetime.now())
        if user_is_excist(user_all_list,member) == False:
            print(user_all_list)
            user_all_list.append(member)
            json.dump(user_detail,user_detail_file,ensure_ascii=False)
    return user_detial_id,user_all_list



def group_detail(group_detial_file,i,group_number,group_name,group_user_number,url):
    group_detail = {}
    group_detail['auto_id'] = i
    group_detail['group_id']= group_number
    group_detail['group_name']= group_name
    group_detail['group_url']= url
    group_detail['group_user_number']= group_user_number
    group_detail['group_type'] = 1
    group_detail['data_source'] = 'TRS'
    group_detail['update_time'] = str(datetime.now())
    group_detail['crawler_time'] = str(datetime.now())
    group_detail['intime'] = str(datetime.now())
    json.dump(group_detail,group_detial_file,ensure_ascii=False) 

def group_relation(group_relation_file,user_relation_id,group_number,member_list,first_time,last_time,relation_all_list):
    for member in member_list:
        group_relation ={}
        group_relation['group_id']= group_number
        group_relation['user_name']= member
        
        user_relation_id =user_relation_id+1
        group_relation['auto_id'] = user_relation_id
        group_relation['md5'] = group_number
        
        group_relation['first_time']= first_time[member]
        group_relation['last_time']= last_time[member]
        group_relation['group_type'] = 1
        group_relation['data_source'] = 'TRS'
        group_relation['update_time'] = str(datetime.now())
        group_relation['crawler_time'] = str(datetime.now())
        group_relation['intime'] = str(datetime.now())
        if group_relation_is_excist(relation_all_list,group_number,member) == False:
            #print(relation_all_list)
            relation_all_list.append({'group_id':group_number,'user_name':member}) 
            json.dump(group_relation,group_relation_file,ensure_ascii=False)
        
    return user_relation_id,relation_all_list


def group_info(group_info_file,content_list,date,Massage_id,group_number,sender_type,true_time,data_id_list,user_name):
    if len(data_id_list) == 1:
        messages = {}
        Massage_id = Massage_id+1
        messages['message_id'] = data_id_list[0]
        messages['user_name'] = user_name
        
        messages['auto_id'] = Massage_id
        messages['md5'] = group_number+str(data_id_list[0])
        messages['group_id'] = group_number
        
        messages['group_type'] = 1
        messages['sender_type'] = sender_type
        
        messages['content'] = content_list
        messages['pubdate'] = date
        messages['pubtime'] = true_time
        messages['data_source'] = 'TRS'
        messages['update_time'] = str(datetime.now())
        messages['crawler_time'] = str(datetime.now())
        messages['intime'] = str(datetime.now())
        json.dump(messages,group_info_file,ensure_ascii=False) 
    else:
        for data in data_id_list:
            messages = {}
            Massage_id = Massage_id+1
            messages['message_id'] = data
            messages['user_name'] = user_name
            
            messages['auto_id'] = Massage_id
            messages['md5'] = group_number+str(data)
            messages['group_id'] = group_number
            
            messages['group_type'] = 1
            messages['sender_type'] = sender_type
            
            messages['content'] = content_list[data_id_list.index(data)]
            messages['pubdate'] = date
            messages['pubtime'] = true_time
            messages['data_source'] = 'TRS'
            messages['update_time'] = str(datetime.now())
            messages['crawler_time'] = str(datetime.now())
            messages['intime'] = str(datetime.now())
            json.dump(messages,group_info_file,ensure_ascii=False) 
    return Massage_id

'''
初始化每个用户第一次发言时间
'''       
def init_first_time(member_list):
    first_time = {}
    first_time['Auto-response'] = ''
    for member in member_list:
        first_time[member] = ''
    return first_time

'''
初始化每个用户最后发言时间
'''
def init_last_time(member_list):
    last_time = {}
    last_time['Auto-response'] = ''
    for member in member_list:
        last_time[member] = ''
    return last_time


'''
记录第一次发言时间
'''   
def recode_first_time(first_time,user_name,date,true_time):
    if first_time[user_name] == '':
        first_time[user_name] = str(date)+' '+str(true_time)
    return first_time

'''
记录最后一次发消息时间
'''
def recode_last_time(last_time,user_name,date,true_time):
    last_time[user_name] = str(date)+' '+str(true_time)
    return last_time

def user_is_excist(user_all_list,user_name):
    
    user_name_flag = False
    if user_name in user_all_list:
        user_name_flag = True
    return user_name_flag


def group_relation_is_excist(relation_all_list,group_number,user_name):
    relation_flag = False
    for object in relation_all_list:
        if user_name == object['user_name'] and group_number == object['group_id']:
            relation_flag = True
            break
    return relation_flag

    

'''
依次遍历div,并从中获取需要的内容
'''
def read_div(div_list,file,group_number,is_group,group_name,group_user_number,i,url,Massage_id,member_list,user_detail_file,group_detial_file,group_relation_file,group_info_file,user_detial_id,user_relation_id,user_all_list,relation_all_list,group_list,flag):
    #group_all_information = {}  # json中存入的字典
    first_time = init_first_time(member_list)
    last_time = init_last_time(member_list)
     # 判断用户是否已经存在，若不存在才存储
    
    user_detial_id,user_all_list = user_detail(user_detail_file,member_list,user_detial_id,user_all_list)
    #print(group_list,flag)
    if group_number not in group_list:
        #print('111')
        group_list.append(group_number)
        flag = init_flag(flag,group_number)
        group_detail(group_detial_file,i,group_number,group_name,group_user_number,url)
    sleep_time()
    start_index = int(flag[group_number])
    for div in div_list:
        # 这里每一天的聊天记录是一个div，class为position-relative
        #soup = BeautifulSoup(div.get_attribute('innerHTML'),'html.parser')
        # 获取消息发送的时间
        date = div.find_element_by_css_selector('div[class="chatsys-content"]')
        date = date.get_attribute('textContent').strip()
        # 获取聊天消息的主体，每一条消息为一个div，但是同一个用户连续发送的消息在一个div中
        chat_content = div.find_elements_by_css_selector('div[class="chat-content"]')
        # 遍历消息主体
        for content_main in chat_content[start_index:]:
            flag[group_number] = int(flag[group_number])+1 
            # 获取用户名称
            user_name = content_main.find_element_by_css_selector('div[class="chat-header"]')
            data_ids = content_main.find_elements_by_css_selector('div[class="chat-body"],div[class="chat-body more"]')
            # 获取该用户在该时间段发送的消息
            content_text_div = content_main.find_elements_by_css_selector('div[class="chat-item-text user-select-text"]')
            # 获取发送的表情包及图片
            content_img = content_main.find_elements_by_tag_name('img')
            # 获取发送的语音
            voices = content_main.find_elements_by_css_selector('div[class="chat-item-voice-text"]')
            # 发送消息的具体时间
            time = content_main.find_elements_by_css_selector('div[class="chat-sub"]')
            # 下载音频和图片
            try:
                download = content_main.find_element_by_xpath('.//a[text()="Download"]') 
                download.click()
                download_path = get_download_path()
                sleep_time()
                filename = os.listdir(download_path)[-1]
                print(filename)
            except Exception:
                filename = ''
            user_name,sender_type = user_type(user_name)
            # 同一时间段发送的消息只有一个time，其他为空，所以遍历判断是否有值
            for time1 in time:
                if time1.text.strip() == '':
                    continue
                else:
                    true_time = time1.text.strip()
            # 记录第一次发消息时间和最后一次发消息时间
            first_time = recode_first_time(first_time,user_name,date,true_time)
            last_time = recode_last_time(last_time,user_name,date,true_time)
            content_list = get_text_img_voice(content_text_div,content_img,voices,filename)
            # 记录消息ID
            data_id_list = []
            for data_id in data_ids:
                data_id_list.append(data_id.get_attribute('data-id'))
            date= date_switch(date)
            
            Massage_id = group_info(group_info_file,content_list,date,Massage_id,group_number,sender_type,true_time,data_id_list,user_name)
            #time_dependacy = str(date)+' '+str(true_time)
            # 写进json     
            #json.dump(group_all_information,file,ensure_ascii=False)
   
    # 判断用户关系是否存在，若不存在则存储
    user_relation_id,relation_all_list = group_relation(group_relation_file,user_relation_id,group_number,member_list,first_time,last_time,relation_all_list)   
    return Massage_id,user_detial_id,user_relation_id,user_all_list,relation_all_list,group_list,flag
           
'''
读取配置文件
'''
def open_config_file(path):
    with open(path,'r',encoding='utf-8') as file:
        config = json.load(file)
    return config


'''
判断是用户还是群聊
'''
def group_user_number_tag(driver,group_user_number_tag):
    # 判断是用户还是群
    if group_user_number_tag == []:
        is_group = 'user'
        group_name_tag = driver.find_element_by_css_selector('h4[class="mb-0 text-truncate"]')
        group_name = group_name_tag.text
        group_user_number = ''
    else:
        is_group = 'group'
        group_name_tag = driver.find_element_by_css_selector('h4[class="mb-0 text-truncate cursor-pointer"]')
        group_name = group_name_tag.text
        group_user_number = group_user_number_tag.text
    return is_group,group_name,group_user_number


def get_download_path():
    """获取系统的默认下载路径"""
    if os.name == 'nt': # Windows系统
        download_path = os.path.expanduser("~\\Downloads")
    elif os.name == 'posix': # macOS或Linux系统
        download_path = os.path.expanduser("~/Downloads")
    else:
        download_path = None
    return download_path


'''
获取群成员
'''
def get_group_member(driver,group_member):
    group_member.click()
    sleep_time()
    members = driver.find_elements_by_css_selector('h6[class="text-truncate mb-0"]')
    member_list = []
    for m in members:
        member_list.append(m.text.strip())
    sleep_time()
    close = driver.find_element_by_css_selector('button[class="close"]')
    close.click()
    return driver,member_list

def init_flag(flag,group_number):
    flag[group_number] = 0
    return flag


def close_file(file_name):
    file_name.close()


'''
程序入口
'''
if __name__ == '__main__':
    url = 'https://developers.line.biz/en/'
    path = 'config.json'
    config = open_config_file(path)
    save_path = config['save_path']
    username = config['username']
    password = config['password']
    browser = config['browser']
    driver_path = config['driver_path']
    standing_time = config['standing time']
    user_detial_id = 0
    user_relation_id =0
    flag = {}
    user_all_list = []
    relation_all_list = []
    group_list = []
    user_detail_path = config["user_detail_path"]
    group_detial_path = config["group_detial_path"]
    group_relation_path = config["group_relation_path"]
    group_info_path = config["group_info_path"]
    driver = driver_chat(url,username,password,browser,driver_path)
    file = create_file(save_path)
    
    #group_number = config['group_number']
    Massage_id = 0
    #time_record = []
    while True: 
        user_detail_file = create_file(user_detail_path)
        group_detial_file = create_file(group_detial_path)
        group_relation_file = create_file(group_relation_path)
        group_info_file = create_file(group_info_path)
        group_user_number = driver.find_elements_by_css_selector('a[class="d-flex w-100 justify-content-center"]')
        # 依次遍历每个群聊，并获取其内容
        for i in range(1,len(group_user_number)+1):
            try:
                group = '/html/body/div[2]/div/div[1]/div/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
                #group = '/html/body/div[2]/div/div[1]/div[1]/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
                driver,url1 = get_group_url(driver,group)
                driver.get(url1)
                sleep_time()
                group_number = str(url1)[61:]
                group_user_number_tag_value = driver.find_element_by_css_selector('span[class="cursor-pointer"]')
                group_member = driver.find_element_by_css_selector('div[class="avatar avatar-xs avatar-initials rounded-circle bg-secondary text-white"]')
                sleep_time()
                #print(group_member.get_attribute('class'))
                driver,member_list = get_group_member(driver,group_member)
                #print(member_list)
                is_group,group_name,group_user_number =  group_user_number_tag(driver,group_user_number_tag_value)
                div_list = get_div(driver,url1)
                Massage_id,user_detial_id,user_relation_id,user_all_list,relation_all_list,group_list,flag = read_div(div_list,file,group_number,is_group,group_name,group_user_number,i,url1,Massage_id,member_list,user_detail_file,group_detial_file,group_relation_file,group_info_file,user_detial_id,user_relation_id,user_all_list,relation_all_list,group_list,flag)
                #time_record.append(time_dependacy)
            except Exception:
                continue
        close_file(user_detail_file)
        close_file(group_detial_file)
        close_file(group_relation_file)
        close_file(group_info_file)
        time.sleep(60)
    quit(driver)

