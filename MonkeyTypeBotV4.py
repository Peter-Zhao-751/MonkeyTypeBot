from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pynput
import threading
import os
import random
import multiprocessing

# running the code cause python oop is kinda weird
def runType(speed, acc):
    idiot=monkeyTyper(speed, acc)
    idiot.startup()
    idiot.main()

#main class with the methods that do stuff
class monkeyTyper(webdriver.Chrome):
    def __init__(self,wpm,accuracy):
        # inherating methods from selenium.webdriver.chrome
        super().__init__(service=Service('path to chrome driver'))
        self.get('https://monkeytype.com')
        self.fullscreen_window()
        # custom variables
        self.wpm=wpm
        self.accuracy=accuracy
        self.work=True
        self.pause=False
        self.systemTime=0.015
        # listener on another thread, it listens for abort
        pynput.keyboard.Listener(on_press=self.abortType).start()
        # another thread that looks for an element that appears after the test is done, so it stops typing
        threading.Thread(target=self.check).start()

    # the method that actucally types
    def main(self):
        self.averageLength=4.04
        if self.mode==3:
            self.typingTime=60
        else:
            self.typingTime=self.mode*15
            
        self.errorNum=int((100-self.accuracy)/100*self.wpm*self.averageLength/60*self.typingTime)
        # get the word in a array first so we can start the loop
        array = self.getWords()
        self.work=True
        self.pause=False
        # loop through the words and add new ones once it runs out
        count=0
        while self.work==True:
            while self.pause:
                pass
            if len(array[count])>20:
                array.insert(count+1, " ")
            array[count]=array[count][0]
            
            if self.errorNum>0 and array[count]!=' ':
                array[count]='$'
                self.errorNum-=1
            #the running out thing
            if count>=(len(array)-1) and count>1:
                array+=self.getWords()
            
            if count>=len(array):
                break
            i=array[count]
            # accuracy
            
            self.tapKey(i)
            count +=1
            #print (count)


    # get new words from the HTML of the site
    def getWords(self):
        # the the raw HTML into a list
        answer = self.find_element(By.ID, "words").get_attribute("outerHTML").split("<letter>")
        answer.pop(0)
        return answer

    # other thread that looks for the html
    def check(self):
        while True:
            try:
                testResult = self.find_element(By.XPATH, '//*[@id="middle"]/div[1]/div[4]/div[1]')
                # check if the element testresult is hidden
                if(testResult.is_displayed()==True):
                    # stops the old typing loop
                    self.pause=True
                    self.work=False
                    time.sleep(2)
                    # clicking the test button
                    self.find_element(By.XPATH, '//*[@id="menu"]/a[1]').click()
                    time.sleep(2)
                    # initing new thread and main typing loop
                    threading.Thread(target=self.check).start()
                    self.typingTime=15
                    self.main()
                    self.systemTime=0.015
                    #self.wpm=random.randint(180, 200)
                    #self.accuracy=random.randint(95, 100)
                    pynput.mouse.Controller().click(pynput.mouse.Button.left)
                    break
                else:
                    pass
            except:
                pass
            time.sleep(0.05)

    def tapKey(self,key):
        # pressing the key
        startTime=time.time()
        ActionChains(self).key_down(key).perform()
        # custon extra delay for space
        if key == " ":
            time.sleep(0.03)
        # normal delay
        #*random.uniform(0.03, 0.05)/0.04*self.accuracy/100
        delayTime=(60/self.wpm/5*random.uniform(0.03, 0.05)/0.04-self.systemTime)
        if delayTime >0:
            time.sleep(delayTime)
        
        # releasing key
        ActionChains(self).key_up(key).perform()
        self.systemTime=time.time()-startTime-delayTime

    def abortType(self, k):
        if k == pynput.keyboard.Key.shift_r:
            print("exit program")
            self.work=False
            self.quit()
            os._exit(0)
        elif k == pynput.keyboard.Key.shift_l:
            self.pause=not self.pause
    def login(self):
        self.find_element(By.XPATH, '//*[@id="menu"]/div[3]').click()
        time.sleep(0.25)
        self.find_element(By.XPATH, '//*[@id="middle"]/div[2]/div[3]/form[1]/input[1]').send_keys("username") 
        time.sleep(0.2)
        self.find_element(By.XPATH, '//*[@id="middle"]/div[2]/div[3]/form[1]/input[2]').send_keys("password") 
        self.find_element(By.XPATH, '//*[@id="middle"]/div[2]/div[3]/form[1]/div[2]').click()
        time.sleep(0.3)
        
    def startup(self):
        # mode is for timed competitions, 1 is 15 seconds, 2 is 30 seconds, 3 is 60 seconds
        #mode = random.randint(1,3)
        self.mode =1
        time.sleep(0.8)
        # cookie click and login
        self.find_element(By.XPATH, '//*[@class="buttons"]/div[1]').click()
        time.sleep(0.05)
        
        self.login()
        
        
        self.find_element(By.XPATH, '//*[@id="menu"]/a[1]').click()
        time.sleep(1)
        
        #this is for the timed competitions, 2 is word, 3 is quote, 4 is zen, 5 is custom
        self.find_element(By.XPATH, '//*[@class="mode"]/div[1]').click()
        time.sleep(0.3)
        # this is to set time: 1 is 15 seconds, 2 is 30 seconds, 3 is 60 seconds
        self.find_element(By.XPATH, '//*[@class="time"]/div['+str(self.mode)+']').click()
        
        #this is a custom time, it is great if you want to get the 2 hours needed for leaderboards
        #self.find_element(By.XPATH, '//*[@class="time"]/div[5]').click()
        #time.sleep(0.1)
        #self.find_element(By.XPATH, '//*[@id="customTestDurationPopup"]/input[1]').send_keys("600")
        #time.sleep(0.1)
        #self.find_element(By.XPATH, '//*[@id="customTestDurationPopup"]/div[4]').click()
        
        #this is to set the text length, if you chose 2 in the first selection 1 is 10 words, 2 is 25 words, 3 is 50 words, 4 is 100 words, 5 is custom
        #self.find_element(By.XPATH, '//*[@class="wordCount"]/div[1]').click() # 10 words
        time.sleep(1.6)
        

# main loop andstuff
if __name__=='__main__':
    runType(200, 100)
