from config import config
from bs4 import BeautifulSoup
import traceback
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import uuid
from datetime import datetime

from config import config

def get_target_config(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except:
        traceback.print_exc()
        return {}


def get_url_content(target_link, m_header):
    try:
        # use_header = m_header
        
        # if target_link.get('header') is not None:
        #     use_header = target_link['header']

        # response = requests.get(url=target_link['url'],headers=use_header)
        # response.raise_for_status()

        # soup = BeautifulSoup(response.text,'html.parser')

        #using selenium
        chrome_options = Options()
        service = Service('/usr/local/bin/chromedriver') 
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(target_link['url'])
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            time.sleep(2)
            # Cuộn xuống dưới cùng của trang
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Tính toán chiều cao mới của trang và so sánh với chiều cao cũ
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        time.sleep(5) 
        page_source = driver.page_source
        driver.quit()
        soup = BeautifulSoup(page_source, 'html.parser')

        return soup

    except:
        traceback.print_exc()
        return None

def extract_data(soup: BeautifulSoup, rules):
    try:
        rs = {}
        for rule in rules:
            extract_data_with_rule(soup, rule, rs)        
        return rs
    except:
        traceback.print_exc()
        return rs

def extract_data_with_rule(soup: BeautifulSoup, rule, rs):
    try:
        soup_at_location = extract_data_at_location(soup=soup, location= rule.get("location"))
        #get the main string
        s = soup_at_location.decode_contents()

        extractors = rule.get('extractors')
        for ext in extractors:
            extract_data_with_extract(s,rs,ext)
        return rs
    except:
        traceback.print_exc()
        return rs

def extract_data_at_location(soup: BeautifulSoup, location):
    try:
        res_tag = soup
    
        for l in location:
            location_tag =l['tag']
            location_index = l['tag_index']
            if l.get('attribute') is not None:
                att_type = l['attribute']['att_type']
                att_value = l['attribute']['att_value']
                
                # if " " in att_value:
                #     tmp_value = att_value
                #     att_value = tmp_value.split(" ")

                if att_type == 'id':
                    res_tag = res_tag.find(id= att_value)
                elif att_type == 'class':
                    res_tag = res_tag.find_all(location_tag, class_= att_value)[location_index]    
                else:
                    res_tag = res_tag.find_all(location_tag)[location_index]    
            else:
                res_tag = res_tag.find_all(location_tag)[location_index]
        
        return res_tag

    except:
        traceback.print_exc()
        return None

def extract_data_with_extract(s: str, rs, extrctr, stop_tail = None ):
    try:
        field_name = extrctr.get("field_name")
        extractors_start = extrctr.get("start")
        extractors_end = extrctr.get("end")

        #define type
        child_extractors = extrctr.get("extractors")
        result_is_array = extrctr.get("isArray")

        #check tail:
        if stop_tail is not None:
            st = s.find(stop_tail)
            if (st <0) and stop_tail != "ignore":
                return s
            
            first_start = s.find(extractors_start[0].get("value"))
            if first_start < 0:
                return s
            
            if st < first_start and stop_tail != "ignore":
                return s

        tmp_str = s

        #dang list
        if result_is_array == True:
            rs[field_name] =[]
            
            before_str = tmp_str
            tmp_obj = {}
            for ext in child_extractors:
                after_str = extract_data_with_extract(tmp_str,tmp_obj,ext) 
            
            rs[field_name].append(tmp_obj)
            
            while (len(after_str) < len(before_str)):
                new_obj = {}
                before_str = after_str
                for ext in child_extractors:
                    after_str = extract_data_with_extract(before_str,new_obj,ext,extractors_end[-1].get("value") )
                if len(new_obj) >0:
                    rs[field_name].append(new_obj)

        #dang object
        if (result_is_array == False ) and (len(child_extractors) >0):
            rs[field_name] = {}
            after_str = ""
            for ext in child_extractors:
                after_str = extract_data_with_extract(s,rs[field_name],ext)

        #value:
        if (result_is_array == False) and (len(child_extractors) == 0):
            after_start_string = s
            for opr in extractors_start:
                after_start_string = process_extractor_operator(after_start_string, opr)

            remove_end_string = after_start_string
            for opr in extractors_end:
                remove_end_string = process_extractor_operator(remove_end_string, opr)
            rs[field_name] = remove_end_string.strip()
            
            #trả lại đuôi
            return after_start_string[after_start_string.find(remove_end_string) + len(remove_end_string):]
        
    except:
        traceback.print_exc()
        return s

def process_extractor_operator(s: str, oprt, isList = None):
    try:

        extract_operator = oprt.get('operator')
        operator_value = oprt.get('value')

        index_operator_value = s.find(operator_value)

        if extract_operator == 'SkipTo':
            if index_operator_value == -1:
                return s
            rs_s = s[index_operator_value + len(operator_value):].strip()
            return rs_s

        if extract_operator == 'BackTo':
            if index_operator_value == -1:
                return s
            rs_s = s[:index_operator_value].strip()
            return rs_s

        return s
    except:
        traceback.print_exc()
        return s

def save_file(rs):
    try:
        print(rs)
        unique_id = str(uuid.uuid4())
        ts = datetime.now().timestamp()

        file_name=f"./results/{str(ts)}_{unique_id}.json"
        with open(file_name, 'w') as json_file:
            json.dump(rs, json_file,ensure_ascii=False, indent=4)

    except:
        traceback.print_exc()

if __name__ == '__main__':
    print("Direct soup")
    targetConfig =  get_target_config(config.get("TARGETCONFIG","FILEPATH"))
    lnks = targetConfig.get("Target_links")
    hd = targetConfig.get("Modified_hearder")

    # for lnk in lnks:

    # the_soup = get_url_content(lnk, hd)
    soup_path = config.get("TARGETCONFIG","SOUPPATH")
    with open(soup_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    the_soup = BeautifulSoup(html_content, 'html.parser')
    # print(the_soup.get_text)
    rs = extract_data(the_soup,targetConfig.get("rules"))
    save_file(rs)
    time.sleep(5)