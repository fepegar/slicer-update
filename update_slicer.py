#!/usr/bin/env python

import os
import re
import time
import shutil
import tempfile
import urllib2
import subprocess
from sys import platform as _platform

from bs4 import BeautifulSoup




def getDownloadURLAndRevisionNumber(version):
    """
    version can be 'stable' or 'nightly'
    """
    SLICER_DOWNLOAD_URL = 'http://download.slicer.org'

    response = urllib2.urlopen(SLICER_DOWNLOAD_URL)
    html = response.read()
    parsed = BeautifulSoup(html, "lxml")
    buttons = parsed.findAll('a')

    indicesMap = {'win32': 1,
                  'darwin': 2,
                  'linux': 3,
                  'linux2': 3}

    buttonIndex = indicesMap[_platform]

    if version == 'nightly':
        buttonIndex += 3

    button = buttons[buttonIndex]
    downloadURL = SLICER_DOWNLOAD_URL + button.get('href')

    buttonText = button.getText()
    p = r'revision (\d+)'
    revisionNumberString = re.findall(p, buttonText)[0]

    return downloadURL, revisionNumberString


def downloadSlicer(url, outputDir):
    # Set the URL
    response = urllib2.urlopen(url)

    # Download the data
    html = response.read()

    extMap = {'win32': '.exe',
              'darwin': '.dmg',
              'linux': '.tar.gz',
              'linux2': '.tar.gz'}

    outputPath = os.path.join(outputDir, 'Slicer' + extMap[_platform])
    with open(outputPath, 'wb') as f:
        f.write(html)
    return outputPath


def installSlicer(filepath):
    if _platform in ('linux', 'linux2'):
        pass  # TODO
    elif _platform == 'darwin':
        cmd = ['hdiutil', 'attach', filepath]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()

        mountDir = output[0].split()[-1]

        print 'Mount directory:', mountDir

        slicerFilename = 'Slicer.app'
        slicerAppSrcPath = os.path.join(mountDir, slicerFilename)
        slicerAppDstPath = os.path.join('/Applications', slicerFilename)
        if os.path.isdir(slicerAppDstPath):
            shutil.rmtree(slicerAppDstPath)
        shutil.copytree(slicerAppSrcPath, slicerAppDstPath)
        cmd = ['hdiutil', 'detach', mountDir]
        subprocess.call(cmd)

    elif _platform == 'win32':
        pass


def main():
    version = 'nightly'

    tempDir = tempfile.mkdtemp()

    startTime = time.time()
    print 'Updating Slicer: {}'.format(time.asctime(time.localtime(time.time())))
    downloadURL, revisionNumberString = getDownloadURLAndRevisionNumber(version)
    print 'Downloading nightly build number {} from {}...'.format(revisionNumberString, downloadURL)
    tempPath = downloadSlicer(downloadURL, tempDir)
    installSlicer(tempPath)

    endTime = int(time.time() - startTime)
    m, s = divmod(endTime, 60)
    print 'Operation finished in {} minutes and {} seconds\n\n'.format(m, s)

    shutil.rmtree(tempDir)


if __name__ == '__main__':
    main()

