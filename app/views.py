"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )
def queryFlow(request):
    assert isinstance(request, HttpRequest)
    import urllib.request
    import requests
    import time
    import datetime
    from django.http import HttpResponse
    from bs4 import BeautifulSoup
    from app.models import FlowQueryLog
    from requests.auth import HTTPBasicAuth

    FLOW_LIMIT = 4500

    try:
        headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':'network.ntust.edu.tw',
            'Origin':'http://network.ntust.edu.tw',
            'Referer':'http://network.ntust.edu.tw/flowstatistical.aspx',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'
        }
        class MyOpener(urllib.request.FancyURLopener):
            version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17'
        myopener = MyOpener()
        url = 'http://network.ntust.edu.tw/flowstatistical.aspx'
        mmonth = time.strftime("%m")
        if mmonth[0] == '0':
            month = mmonth[1]
        else:
            month = mmonth
        dday = time.strftime("%d")
        if dday[0] == '0':
            day = dday[1]
        else:
            day = dday
        # first HTTP request without form data
        f = myopener.open(url)
        soup = BeautifulSoup(f)
        # parse and retrieve two vital form values
        viewstate = soup.select("#__VIEWSTATE")[0]['value']
        eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']
        viewstategenerator = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
        formData = (
            ('__EVENTVALIDATION', eventvalidation),
            ('__VIEWSTATE', viewstate),
            ('__VIEWSTATEGENERATOR',viewstategenerator),
            ('__EVENTTARGET', ''),
            ('__EVENTARGUMENT', ''),
            ('__LASTFOCUS', ''),
            ('ctl00$ContentPlaceHolder1$txtip','140.118.21.25'),
            ('ctl00$ContentPlaceHolder1$dlmonth',month),
            ('ctl00$ContentPlaceHolder1$dlday',day),
            ('ctl00$ContentPlaceHolder1$dlcunit','1048576'),
            ('ctl00$ContentPlaceHolder1$btnview','檢視24小時流量')
        )
        encodedFields = urllib.parse.urlencode(formData)
        # second HTTP request with form data
        f = myopener.open(url, encodedFields)
        lines = f.readlines()
        totalString = b"\xe7\xb8\xbd\xe8\xa8\x88"
        def getInt(line):
            return int(line.split(b" (M)")[0].split(b' ')[-1].replace(b",", b""))
        for i in range(len(lines)):
            if totalString in lines[i]:
                #print ("download:\t", getInt(lines[i+2]))
                download = getInt(lines[i+2])
                #print ("upload:\t\t", getInt(lines[i+4]))
                upload = getInt(lines[i+4])
                #print ("total:\t\t", getInt(lines[i+6]))
                total = getInt(lines[i+6])
                break
    except:
        download = -1
        upload = -1
        total = -1
    if FlowQueryLog.objects.latest('time').note == 'cutoff':
        newNote = 'cutoff'
    else:
        newNote = str(f.status)
    FlowQueryLog.objects.create(
        time = datetime.datetime.utcnow()+datetime.timedelta(hours=+8), 
        download = download,
        upload = upload,
        total = total,
        note = newNote
        )
    #FlowQueryLog.objects.earliest('time').delete()
    query = FlowQueryLog.objects.latest('time')
    if (total > FLOW_LIMIT and newNote != 'cutoff') or (total < FLOW_LIMIT and newNote == 'cutoff'):
        if total > FLOW_LIMIT:
            query.note = 'cutoff'
            query.save()
            ssid = 'Network_is_GG'
            policy = '2'
        else:
            query.note = '200'
            query.save()
            ssid = 'NTUST-ECE'
            policy = '0'
        payload = {
        'tmenu':'wirelessconf',
        'smenu':'basicsetup',
        'act':'apply',
        'wl_mode':'0',
        'modechange':'0',
        'channel_width':'40',
        'auto_channel':'0',
        'run':'1',
        'wireless_mode':'0',
        'ssid':ssid,    #SSID名稱
        'bssid':'',
        'mode':'6',
        'country':'TW',
        'channel':'11.9',
        'broadcast_ssid':'1',
        'wmm':'1',
        'auth_type':'10',
        'encrypt_type':'4',
        'wpapsk_key':'0988620735',    #密碼
        'key_input':'0',
        'default_key':'1',
        'key_length_desc':'',
        'wep_key1':'',
        'wep_key2':'',
        'wep_key3':'',
        'wep_key4':''
        }
        username = 'admin'
        password = 'admin'
        f = requests.get("http://140.118.21.25:8080/cgi-bin/timepro.cgi", 
            params = payload, auth=HTTPBasicAuth(username, password))

        payload = {
            'tmenu':'wirelessconf',
            'smenu':'macauth',
            'act':'policy',
            'wl_mode':'0',
            'bssidx':'0',
            'policy':policy    # 0=不限制 2=白名單 1=黑名單
        }
        f = requests.get("http://140.118.21.25:8080/cgi-bin/timepro.cgi", 
                params = payload, auth=HTTPBasicAuth(username, password))
    return HttpResponse("download:" + str(download) + "<br>" + 
        "upload:" + str(upload) + "<br>" +
        "total:" + str(total) + "<br>" + 
        "time:" + time.strftime("%a, %d %b %Y %H:%M:%S"))

def collie(request):
    """Renders the collie page."""
    assert isinstance(request, HttpRequest)
    import datetime
    from app.models import FlowQueryLog
    query = FlowQueryLog.objects.latest('time')
    lastQueryTime = query.time
    download = query.download
    upload = query.upload
    total = query.total
    if total < 3500:
        healthy = 'Healthy'
        dangerous = ''
        cutoff = ''
    if total > 3500:
        healthy = ''
        dangerous = 'DANGEROUS'
        cutoff = ''
    if total > 4500:
        healthy = ''
        dangerous = ''
        cutoff = 'CUT-OFF'
    return render(
        request,
        'app/collie.html',
        context_instance = RequestContext(request,
        {
            'healthy': healthy,
            'dangerous':dangerous,
            'cutoff':cutoff,
            'lastQueryTime':lastQueryTime,
            'download':download,
            'upload':upload,
            'total':total,
            'time':datetime.datetime.utcnow()+datetime.timedelta(hours=+8)
        })
    )
