#!/bin/python2
''' A script to dl fanfiction from ffnet'''
import requests as re
import sys
from lxml import html
import subprocess
from optparse import OptionParser
from progressbar import ProgressBar
#TODO Convert random parsing to optparse

# Basics
#
# Url example:
# https://www.fanfiction.net/s/5782108/1/Harry-Potter-and-the-Methods-of-Rationality 
#           domain       /story/story-id/chap-id/fic-name
#
#   All I need is story id.
#
# Step 1:  Get total number of chapters for a fic.
# Step 2:  Get title and author name.
# Step 3:  Put all content in one html file.
# Step 4:  Use calibre to convert the file to required format
#
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

fList = ''
dest = ''
if '-f' in sys.argv:
    fList = sys.argv[sys.argv.index('-f')+1]

if '-d' in sys.argv:
    dest = sys.argv[sys.argv.index('-d')+1]
    if dest[-1] != '/':
        dest += '/'


if '-u' in sys.argv:
    url = sys.argv[sys.argv.index('-u')+1]
else:
    if fList == '':
        print "Please enter a story URL"
        exit(0)

if '-t' in sys.argv:
    fType = sys.argv[sys.argv.index('-t')+1]

    if fType in ['mobi','Mobi','MOBI']:
        filType = 'mobi'
    if fType in ['epub','Epub','EPUB']:
        filType = 'epub'
    if fType in ['pdf','Pdf','PDF']:
        filType = 'pdf'
else:
    filType = 'mobi'

def getStory(storyUrl,progbar, storynumber):
    # Find the story id
    storyIdEnd = storyUrl[storyUrl.find('/s/')+10]
    if storyIdEnd == '/':
        print '  Story url found.'
        storyId = storyUrl[storyUrl.find('/s/')+3:storyUrl.find('/s/')+10]
    else:
        print '  Story id is longer than normal. '
        storyId = storyUrl[storyUrl.find('/s/')+3:storyUrl.find('/s/')+11]


    # Get number of chapters
    chapCount = 1
    chapNum = 1
    author = ''
    title = ''
    finalStory = ''
    summary = ''
    stats = ''
    statLine  = []
    notFoundText = 'Chapter not found. Please check to see you are not using an outdated url.' 
    chap_url = 'https://www.fanfiction.net/s/%s/%s/' % (storyId,str(chapCount))
    chap = re.get(chap_url)

    print "Overall Progress:",
    print progbar

    # Loop till you get notfoundtext.
    # Add all the relevant text to finalStory
    while (html.fromstring(chap.text).xpath('/html/body/div/span/text()[2]')) != notFoundText.split('%'):
        

        # Get author ,summary and title
        if title == '':
            title = html.fromstring(chap.text).xpath('//*[@id="profile_top"]/b')[0].text
            finalStory += "<h1>" + title + "</h1><br/>"
        if author == '':
            author = html.fromstring(chap.text).xpath('//*[@id="profile_top"]/a[1]')[0].text
            finalStory += "<h2>" + title + "</h2><br/>"
            finalStory += "<h3>" + author + "</h3><br/>"
        if summary == '':
            summary = html.fromstring(chap.text).xpath('//*[@id="profile_top"]/div')[0].text
            finalStory += "Summary: <div>" + summary + "</div><br/>"
        if stats == '':
            try:
                # When there's a profile pic, it's 4, else , it's 3.
                if html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span[3]/text()[1]') == ['Rated: ']:
                    spanNum = 3
                else:
                    spanNum = 4
            except:
                spanNum = 4

            try:
                statLine = html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/text()[1]')
                statLine += html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/a[1]')[0].text
                statLine += html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/text()[2]')
                statLine += html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/a[2]')[0].text
                statLine +=html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/text()[3]')
                statLine +=html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/text()[4]')
                statLine +=html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/span[2]')[0].text
                statLine +=html.fromstring(chap.text).xpath('//*[@id="profile_top"]/span['+str(spanNum)+']/text()[5]')
            except:
                statLine = 'Not Found'

            stats = ''.join(statLine)
            try:
                chapNum = chap.text[chap.text.index('Chapters:')+10:chap.text.index('- Words')-1]
            except:
                # If there's no "Chapters" text, that means one shot.
                chapNum = str(1)

            print ''
            print "Title of the Story  :  " + title
            print "Author of the Story :  " + author
            print "Chapters            :  " + chapNum
            print "Summary             :  " + summary
            print ''
            print "Statistics          :  " + stats
            chapProg = ProgressBar(**{
                'end':int(chapNum),
                'width':30,
                })
            chapProg += 1

            finalStory += "Statistics<div>" + stats + "</div><br/>"
        
        if chapCount == 1:
            print "Story   Chapter   Story Name              Progress"
            print str(storynumber) + ".      " + str(chapCount) + " of " + str(chapNum) + "  " + title,
        sys.stdout.write('\r' + str(storynumber) + ".      " + str(chapCount) + " of " + str(chapNum) + "  " + title + "  " + str(chapProg))
        sys.stdout.flush()
        # Add chapter text to final story
        finalStory += "<h2>Chapter " + str(chapCount) + "</h2>"
        finalStory += html.tostring((html.fromstring(chap.text).xpath('//*[@id="storytext"]'))[0])
        

        chapCount += 1
        chapProg += 1
        chap = re.get('https://www.fanfiction.net/s/%s/%s/' % (storyId,str(chapCount)))


    # Open a html file, and put this in the file
    filTitle = title.replace(' ','_')
    htfil = open(filTitle + '.html','w+')
    htfil.write(finalStory.encode('utf-8'))
    htfil.close()

    # Convert the book using ebook-convert - (Does most of the job for now)
    print "\nConverting the file......"
    subprocess.call(['ebook-convert',filTitle + '.html',dest + title + '-' + author + '.' + filType],stdout=DEVNULL, stderr = subprocess.STDOUT)
    subprocess.call(['rm',filTitle + '.html'])
    print "Saved file to " + dest + title + '-' + author + '.' + filType
    print progbar

if __name__ == '__main__':
    if fList == '':
        print "Started getting story from " + url
        getStory(url,0,1)
        print "    Completed."
        print ''
    else:
        try:
            storyList = open(fList,'r')
        except:
            print "Error opening the file."
        
        sList = storyList.read().split('\n')
        progressBarOpt = {
                'end':len(sList),
                'width':50,
                #'format':'%(progress)s%% [%(fill)s%(blank)s]'
        }
        prog = ProgressBar(**progressBarOpt)
        for line in sList:
            storyNum = sList.index(line) +1
            if line != '':
                print ''
                print "Started getting story from " + line
                getStory(line,prog,storyNum)
                prog += 1
                print "    Completed."
                print ''

#TODO  Print a status at the end
