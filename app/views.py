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
    import time
    import datetime
    from django.http import HttpResponse
    from bs4 import BeautifulSoup
    from app.models import FlowQueryLog

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
    FlowQueryLog.objects.create(
        time = datetime.datetime.utcnow()+datetime.timedelta(hours=+8), 
        download = download,
        upload = upload,
        total = total,
        note = str(f.status)
        )
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
