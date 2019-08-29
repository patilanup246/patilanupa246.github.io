import requests
import lxml
from lxml import html
import re
from selenium import webdriver
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from random import uniform, randint
import sys
import time
import random
import argparse
from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.keys import Keys

# If this script no longer fetches any results check the XPath

f = open('youtube.csv','w')
f.write('url,name,subscribers,views,email,email_get_from')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search', help='Enter the search term')
    parser.add_argument('-p', '--pages', default='1', help='Enter how many pages to scrape (1 page = 100 results)')
    return parser.parse_args()

def start_browser():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugin-port=9222")
    options.add_argument("--incognito")

    br = webdriver.Chrome(chrome_options=options)
    #br = webdriver.Firefox()

    br.implicitly_wait(10)
    return br

def get_ua():
    ua_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0']
    ua = random.choice(ua_list)
    return ua

def scrape_results(br):
    # Xpath will find a subnode of h3, a[@href] specifies that we only want <a> nodes with
    # any href attribute that are subnodes of <h3> tags that have a class of 'r'

    strhtml = br.page_source
    # strhtml = strhtml.decode('utf-8')

    if 'Sorry, Google does not serve more than 1000 results for any query.' in strhtml:
        return False

    response = html.fromstring(br.page_source)
    links = response.xpath("//div[@class='r']/a[contains(@href,'youtube.com/')]/@href")
    results = links
    main_result = []

    for resu in results:
        if 'translate.google.com' not in resu:
            main_result.append(resu)
    # for link in links:
    #     #title = link.text.encode('utf8')
    #     url = link.xpath(".//@href")
    #     title_url = url
    #     results.append(title_url)
    if main_result == []:
        return False
    return main_result

def go_to_page(br, page_num, search_term):
    page_num = page_num - 1
    start_results = page_num * 100
    start_results = str(start_results)
    url = 'https://www.google.com/webhp?#num=100&start='+start_results+'&q='+search_term
    #url = 'https://www.google.com/search?q=site:youtube.com/channel+%22menswear%22'
    print('[*] Fetching 100 results from page '+str(page_num+1)+' at '+url)
    br.get(url)
    time.sleep(10)


def check_exists_by_xpath(br, xpath):
    try:
        br.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def wait_between(a,b):
	rand=uniform(a, b)
	sleep(rand)

def main():
    #args = parse_args()
    br = start_browser()
    # if not args.search:
    #     sys.exit("[!] Enter a term or phrase to search with the -s option: -s 'dan mcinerney'")
    search_term = 'site:youtube.com/channel "streetwear"'
    page_num = 1

    all_results = []
    next_page = True
    while next_page:
        go_to_page(br, page_num, search_term)
        titles_urls = scrape_results(br)
        #titles_urls = ['https://www.youtube.com/user/THESNEAKERADDICT/about','https://www.youtube.com/channel/UCJwmLbwgbSxzH4EbBLkXYAw/about']
        if titles_urls == False:
            next_page = False
            print("................If page finish or captch error............")
        else:
            for title in titles_urls:
                print(title)
                #all_results.append(title)

                if '/channel/' in title:
                    url = title.split('youtube.com/channel/',1)[1]
                    if '/' in url:
                        url = url.split('/',1)[0]
                    main_url = 'https://www.youtube.com/channel/' + url + '/about'
                if '/user/' in title:
                    url = title.split('youtube.com/user/', 1)[1]
                    if '/' in url:
                        url = url.split('/', 1)[0]

                    main_url = 'https://www.youtube.com/user/'+url+'/about'

                try:
                    br.get(main_url)
                    try:
                        strhrml_chennel = br.page_source
                        response_chennel = html.fromstring(strhrml_chennel)
                        subscribers = response_chennel.xpath('//*[@id="subscriber-count"]/text()')
                        if len(subscribers) > 0:
                            subscribers = str(subscribers[0]).replace('subscribers','').strip()
                        views = response_chennel.xpath("//yt-formatted-string[contains(text(),' views')]/text()")
                        if len(views) > 0:
                            views = str(views[0]).replace('views','').strip()

                        name = response_chennel.xpath('//*[@id="channel-title"]/text()')
                        if len(name) > 0:
                            name = str(name[0]).strip()
                        print(name)
                        print(subscribers)
                        print(views)
                    except Exception as e:
                        name = ''
                        subscribers = ''
                        views = ''

                    descript = ''
                    email = ''

                    try:
                        br.find_element_by_xpath("//yt-formatted-string[contains(text(),'View email address')]").click()
                        time.sleep(5)
                        mainWin = br.current_window_handle
                        time.sleep(2)

                        # move the driver to the first iFrame
                        br.switch_to_frame(br.find_elements_by_tag_name("iframe")[0])
                        # driver.find_element_by_xpath('//*[@class="recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox"]').click()
                        # driver.find_element_by_xpath('//*[@id="recaptcha-anchor"]').click()
                        #//*[@id="recaptcha-anchor"]
                        # *************  locate CheckBox  **************
                        CheckBox = WebDriverWait(br, 10).until(
                            EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
                        )
                        # *************  click CheckBox  ***************
                        wait_between(0.5, 0.7)
                        # making click on captcha CheckBox
                        CheckBox.click()

                        time.sleep(5)
                        br.find_element_by_xpath("//span[contains(text(),'Submit')]").click()
                        time.sleep(5)
                        strhrml_email = br.page_source
                        response_email = html.fromstring(strhrml_email)
                        email = response_email.xpath('//*[@id="email-container"]/a/text()')
                        if len(email) > 0:
                            email = str(email[0]).strip()
                        print(email)
                        descript = 'button'
                    except Exception as e:
                        email = ''
                        descript = ''

                    if email == '':
                        email = re.search(r'[\w\.-]+@[\w\.-]+', strhrml_chennel)
                        email = email.group(0)
                        descript = 'page'
                except Exception as e:
                    email = ''
                    descript = ''
                print(email)
                print(descript)
                if name != '':
                    f.write('\n')
                    f.write('url,name,subscribers,views,email,email_get_from')
                    f.write(str(main_url)+','+str(name)+','+str(subscribers)+','+str(views)+','+str(email)+str(descript))

            page_num = page_num + 1
    br.quit()
    f.close()

if __name__ == "__main__":
    main()























# driver = webdriver.Chrome()
#
# res = requests.get("https://www.google.com/search?q=site:youtube.com/channel+%22streetwear%22")
#
# try:
#     strhrml = res.text
#     response = html.fromstring(strhrml)
#     All_chennel = response.xpath('//*[@class="ext"]/@href')
#     print(All_chennel)
# except Exception as e:
#     print(e)
#
# def wait_between(a,b):
# 	rand=uniform(a, b)
# 	sleep(rand)
#
# for chennel in All_chennel:
#     driver = webdriver.Chrome('/home/nitin/PycharmProjects/test/chromedriver')
#     driver.get(str(chennel).replace('videos','about'))
#     try:
#         strhrml_chennel = driver.page_source
#         response_chennel = html.fromstring(strhrml_chennel)
#         subscribers = response_chennel.xpath('//*[@id="subscriber-count"]/text()')
#         if len(subscribers) > 0:
#             subscribers = str(subscribers[0]).replace('subscribers','').strip()
#         views = response_chennel.xpath("//yt-formatted-string[contains(text(),' views')]/text()")
#         if len(views) > 0:
#             views = str(views[0]).replace('subscribers','').strip()
#         print(subscribers)
#         print(views)
#     except Exception as e:
#         print(e)
#
#     try:
#         driver.find_element_by_xpath("//yt-formatted-string[contains(text(),'View email address')]").click()
#         time.sleep(5)
#         mainWin = driver.current_window_handle
#         time.sleep(2)
#
#         # move the driver to the first iFrame
#         driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])
#         # driver.find_element_by_xpath('//*[@class="recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox"]').click()
#         # driver.find_element_by_xpath('//*[@id="recaptcha-anchor"]').click()
#         #//*[@id="recaptcha-anchor"]
#         # *************  locate CheckBox  **************
#         CheckBox = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
#         )
#         # *************  click CheckBox  ***************
#         wait_between(0.5, 0.7)
#         # making click on captcha CheckBox
#         CheckBox.click()
#
#         time.sleep(5)
#         driver.find_element_by_xpath("//span[contains(text(),'Submit')]").click()
#         time.sleep(5)
#         strhrml_email = driver.page_source
#         response_email = html.fromstring(strhrml_email)
#         email = response_email.xpath('//*[@id="email-container"]/a/text()')
#         if len(email) > 0:
#             email = str(email[0]).strip()
#         print(email)
#
#     except Exception as e:
#         print(e)

