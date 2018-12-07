# time:2018-11-27

# 通过selenium 实现12306的模拟登陆和抢票订票等功能的实现。

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Qiangpiao():
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path=r"D:\pyxiangguan\chromdrive\phantomjs-2.1.1-windows\bin\phantomjs")
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.personal_page_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.search_url = 'https://kyfw.12306.cn/otn/leftTicket/init'

    # 输入相关的出发地点，目的地，出发时间，车次等信息
    def _wait(self):
        self.from_station = input('请输入出发地：')
        self.to_station = input('请输入目的地：')
        self.train_time = input('请输入要出发的时间（格式如：2018-01-01）：')
        # self.train_time = '2018-12-01'
        self.passengers = input('请输入乘客姓名：').split(',')
        # self.passengers = ['XXX',]
        self.trains = input('请输入要坐的车次：').split(',')
        # self.trains = ['G121', 'G123']

    # 登录页面
    def _login(self):
        self.driver.get(self.login_url)
        time.sleep(1)
        # self.driver.save_screenshot('login.png')
        # 填写登录用户户名和密码
        username = self.driver.find_elements_by_id('username')[0]
        print('username:',username)
        username.send_keys('187XXXXXXXX')
        password = self.driver.find_element_by_id('password')
        password.send_keys('XXXXXXXXXXXX')
        # 验证码点击
        # move_to_element_with_offset(to_element, xoffset, yoffset) ——移动到距某个元素（左上角坐标）多少距离的位置
        # 验证码元素
        captcha = self.driver.find_element_by_class_name('touclick-image')
        # captcha_loction = captcha.location
        # captcha_size = captcha.size
        # print('captcha_loction:',captcha_loction)
        # print('captcha_size:', captcha_size)

        # 需要点击确认的验证码小图片坐标位置，相对于整个验证码图片而言
        captcha_map = {
            1: '50,70',
            2: '120,70',
            3: '190,70',
            4: '260,70',
            5: '50,140',
            6: '120,140',
            7: '190,140',
            8: '260,140',
        }
        # 通过观察保存的网页页面图片来输入验证码相关信息
        self.driver.save_screenshot('验证码第一次.png')
        # 输入验证码需要点击验证的位置 1，2，3，代替
        while True:
            captcha_number_list = input('请输入符合要求验证码位置：（以逗号隔开）').split(',')
            for captcha_number in captcha_number_list:
                zuobiao = captcha_map[int(captcha_number)].split(',')
                ActionChains(self.driver).move_to_element_with_offset(captcha, zuobiao[0], zuobiao[1]).click().perform()
            # time.sleep(1)
            # self.driver.save_screenshot('login_yanzm.png')

            # 点击登录
            login_click = self.driver.find_element_by_id('loginSub')
            login_click.click()
            time.sleep(5)
            # print('url:',self.driver.current_url)
            # 如果验证码第一次验证出现错误，则后面的验证码识别就通过看这张图片，如果正确则进入个人页面
            self.driver.save_screenshot('验证码第N次或者登陆成功.png')
            if self.driver.current_url == self.personal_page_url:
                print('-------登陆成功-------')
                break

    def _order_ticker(self):
        # 跳转到查询余票页面
        self.driver.get(self.search_url)

        # 出发地
        from_station = self.driver.find_element_by_id('fromStationText')
        ActionChains(self.driver).move_to_element(from_station).click(from_station).send_keys(self.from_station).perform()
        # 由于12306需要在查询框里面点击相应出现的出发地或目的地，所以还需要这一步点击确认。
        ActionChains(self.driver).move_to_element_with_offset(from_station, 10,60).click().perform()
        # 目的地
        to_station = self.driver.find_element_by_id('toStationText')
        ActionChains(self.driver).move_to_element(to_station).click(to_station).send_keys(self.to_station).perform()
        ActionChains(self.driver).move_to_element_with_offset(to_station, 10, 60).click().perform()
        # 出发时间
        train_date = self.driver.find_element_by_id('train_date')
        # train_time = input('请输入要出发的时间（格式如：2018-01-01）：')
        self.driver.execute_script("arguments[0].value = '%s';"%self.train_time, train_date)
        value = train_date.get_attribute('value')
        print(value)

        # 查询按钮
        query_ticket = self.driver.find_element_by_id('query_ticket')
        query_ticket.click()
        time.sleep(2)
        self.driver.save_screenshot('查询信息输入完成.png')
        # 在点击了查询按钮后，等待车次信息是否显示出来
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, './/tbody[@id="queryLeftTable"]/tr'))
        )
        # 找到所有没有datatran的属性的tr标签,这些标签存储了车次的相关信息
        tr_list = self.driver.find_elements_by_xpath('.//tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        print(tr_list)
        # 遍历所有满足条件的tr标签
        for tr in tr_list:
            train_number = tr.find_element_by_class_name('number').text
            # print(train_number)
            # print('='*20)
            if train_number in self.trains:
                # 查询二等座票位信息
                left_ticket = tr.find_element_by_xpath('.//td[4]').text
                if left_ticket == '有' or left_ticket.isdigit:
                    print(train_number+left_ticket)
                    order_btn = tr.find_element_by_class_name('btn72')
                    order_btn.click()
                    break
        time.sleep(3)
        self.driver.save_screenshot('预定点击后转换到订单页面.png')

        # 进入订单页面，选择乘客姓名后提交订单
        print('url:',self.driver.current_url)
        passenger_list = self.driver.find_elements_by_xpath("//ul[@id='normal_passenger_id']/li")
        print('passenger_list:',passenger_list)
        for passenger in passenger_list:
            passenger_name = passenger.find_element_by_xpath('./label').text
            # print('passenger_name:',passenger_name)
            if passenger_name in self.passengers:
                passenger_input = passenger.find_element_by_class_name('check')
                passenger_input.click()
        # time.sleep(3)
        # self.driver.save_screenshot('勾选乘客.png')

        # 提交订单信息
        submitOrder = self.driver.find_element_by_id('submitOrder_id')
        submitOrder.click()
        time.sleep(3)
        self.driver.save_screenshot('订单提交后.png')

        # 核对信息后的确认
        qr_submit = self.driver.find_element_by_id('qr_submit_id')
        qr_submit.click()
        time.sleep(4)
        self.driver.save_screenshot('确认订单后.png')


    def run(self):
        self._login()
        self._wait()
        self._order_ticker()

if __name__ == '__main__':
    qiangpiao = Qiangpiao()
    qiangpiao.run()

