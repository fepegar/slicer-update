#!/usr/bin/env python2

import os
import re
import sys
import time
import shutil
import hashlib
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

        print('Mount directory:', mountDir)

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


def createCask(revisionNumber, downloadURL, outputCaskPath, dmgPath=None):
    if dmgPath is None:
        sha256String = ':no_check'
    else:
        sha256String = getSHA256(dmgPath)

    n = downloadURL.split('/')[-1]

    strings = ["cask 'slicer-nightly' do",
               "  version '4.7.0.{},{}'".format(revisionNumber, n),
               "  sha256 '{}'".format(sha256String),
               "  ",
               "  # slicer.kitware.com/midas3 was verified as official when first introduced to the cask",
               "  url 'http://slicer.kitware.com/midas3/download?bitstream=#{version.after_comma}'",
               "  name '3D Slicer Nightly'",
               "  homepage 'https://www.slicer.org/'",
               "  ",
               "  app 'Slicer.app'",
               "end"]
    string = '\n'.join(strings)

    with open(outputCaskPath, 'w') as f:
        f.write(string)


def getSHA256(filepath):
    """
    From https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    """
    hashSHA256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashSHA256.update(chunk)
    return hashSHA256.hexdigest()


def main():
    version = 'nightly'

    startTime = time.time()
    print('Updating Slicer: {}'.format(time.asctime(time.localtime(time.time()))))

    # Create a temporary dir to store the downloaded file
    tempDir = tempfile.mkdtemp()

    # Get download URL from Slicer download page
    downloadURL, revisionNumber = getDownloadURLAndRevisionNumber(version)
    print('Downloading nightly build number {} from {}...'.format(revisionNumber, downloadURL))

    # Download the DMG file
    # tempPath = downloadSlicer(downloadURL, tempDir)

    # # Mount, copy to apps and unmount
    # installSlicer(tempPath)

    # Create a brew cask
    if len(sys.argv) > 1:
        print('Creating cask...')
        outputCaskPath = sys.argv[1]
        createCask(revisionNumber, downloadURL, outputCaskPath, dmgPath=tempPath)

    # Cleanup
    shutil.rmtree(tempDir)

    # Show time
    endTime = int(time.time() - startTime)
    m, s = divmod(endTime, 60)
    print('Operation finished in {} minutes and {} seconds\n\n'.format(m, s))


if __name__ == '__main__':
    main()
