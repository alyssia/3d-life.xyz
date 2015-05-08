#!/usr/bin/env python
# -*- utf-8 -*-
import re,urllib,urllib2,cookielib
 
email = raw_input("your email account: ") #账号
password = raw_input("and password: ") #密码
 
class douban_robot:
 
    def __init__(self):
        self.email = email
        self.password = password
        self.data = {
                "form_email": email,
                "form_password": password,
                "source": "index_nav",
                "remember": "on"
        }
 
        self.login_url = 'http://www.douban.com/accounts/login'
        self.load_cookies()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = [("User-agent","Mozilla/5.0 (Windows NT 6.1)\
        AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11)")]
        self.get_ck()
 
    def load_cookies(self):
        try:
            self.cookie = cookielib.MozillaCookieJar('Cookies.txt')
            self.cookie.load('Cookies_saved.txt')
            print "loading cookies.."
        except:
            print "The cookies file is not exist."
            self.login_douban()
            #reload the cookies.
            self.load_cookies()
 
    def get_ck(self):
        #open a url to get the value of ck.
        self.opener.open('http://www.douban.com')
        #read ck from cookies.
        for c in list(self.cookie):
            if c.name == 'ck':
                self.ck = c.value.strip('"')
                print "ck:%s" %self.ck
                break

        else:
            print 'ck is Empty.'
            self.login_douban()
            #reload the cookies.
            self.load_cookies()
            self.get_ck()
 
    def login_douban(self):
        '''
        login douban and save the cookies into file.
 
        '''
        cookieFile = "Cookies_saved.txt";
        cookieJar = cookielib.MozillaCookieJar(cookieFile);
        #will create (and save to) new cookie file
        # cookieJar.save();
 
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
        #!!! following urllib2 will auto handle cookies
        response = opener.open(self.login_url, urllib.urlencode(self.data))
        html = response.read()
 
        # fp = open("1.html","wb")
        # fp.write(html)
        # fp.close
 
        imgurl = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha"').findall(html)
        if imgurl:
            #download the captcha_image file.
            # urllib.urlretrieve(imgurl[0], 'captcha.jpg')
            print "the captcha_image address is %s" %imgurl[0]
            data = opener.open(imgurl[0]).read()
            f = file("captcha.jpg","wb")
            f.write(data)
            f.close()
 
            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            if captcha:
                vcode=raw_input('图片上的验证码是：')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "登录"
                #验证码验证
                response = opener.open(self.login_url, urllib.urlencode(self.data))
 
        # if response.geturl() == self.login_url:
 
        #     html = opener.open('http://www.douban.com').read()
        #     fp = open("2.html","wb")
        #     fp.write(html)
        #     fp.close
        #     imgurl = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha"').findall(html)
        #     print imgurl
        #     #download the captcha_image file.
        #     urllib.urlretrieve(imgurl[0], 'captcha.jpg')
 
        #     captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
        #     if captcha:
        #         vcode=raw_input('图片上的验证码是：')
        #         self.data["captcha-solution"] = vcode
        #         self.data["captcha-id"] = captcha.group(1)
        #         self.data["user_login"] = "登录"
        #         #验证码验证
        #         response = opener.open(self.login_url, urllib.urlencode(self.data))
 
        #登录成功
        if response.geturl() == "http://www.douban.com/":
            print 'login success !'
            #update cookies, save cookies into file
            cookieJar.save();
        else:
            return False
        return True
 
    def save(self,url, title, time):
        # the HTML note page
        post_data = urllib.urlencode({
            'ck':self.ck,
            })
        request = urllib2.Request(url)
        request.add_header("Referer", url)
        f = self.opener.open(request, post_data)
 
        #marks the start of the note
        startstr = '<div class="note" id="link-report">'
        #marks the end of the note
        endstr = '</div>'
        content = ""
        # Flag, if we are saving the content
        saving = False
        for line in f:
            if saving:
                if endstr in line:
                    saving = False
                    w.write("\nTitle: "+ title + "\nTime: " + time + "\nContent: " + content + "\n")
                    print "Finished: " + title
                    return
                else:
                    content += line
            else:
                start = line.find(startstr)
                if start != -1:
                    content += line[start + len(startstr):]
                    saving = True
 
    def fetch(self,post_url):        
        #print "Start fetching notes from: " + post_url
        post_data = urllib.urlencode({
            'ck':self.ck,
            })
        request = urllib2.Request(post_url)
        request.add_header("Referer", post_url)
        f = self.opener.open(request, post_data)
        title = None
        time = None
        note_url = None
        for line in f:
            # fetch the title and note url
            m = re.match('.*<a title="([^"]*)" href="([^"]*)">(.*)</a>', line)
            if m:
                # UnicodeDecodeError
                #title = h.unescape(m.group(3).decode("utf-8"))
                title = m.group(3)
                note_url = m.group(2)
                continue
            # fetch the time
            m = re.match('.*<span class="pl">([^<]*)</span>', line)
            if m:
                time = m.group(1)
                # save this note to the file
                self.save(note_url, title, time)
                continue
            # fetch the next page of a list of notes
            m = re.match('.*<link rel="next" href="([^"]*)"/>', line)
            if m:
                self.fetch(m.group(1))
            # don't fetch things on the side column
            m = re.match('.*<div class="aside">.*', line)
            if m:
                return
        return None
 
if __name__ == '__main__':
    app = douban_robot()
    fname = "%s.txt" %(raw_input("file name: "))
    xxx = raw_input("people id: ")
    post_url = "http://www.douban.com/people/%s/notes" %xxx
    print post_url
    w = open(fname, "w")
    app.fetch(post_url)
    w.close()
