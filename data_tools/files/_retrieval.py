import os as _os
import ftplib as _ftplib
import urllib as _urllib
import requests as _requests

__all__ = ['get_content_type', 'is_downloadable', 'is_text', 'download_file', 'save_text',
            'is_ftp', 'download_ftp', 'download']


def get_content_type(url):
    """Determines the content type of a URL"""
    h = _requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    return content_type


def is_downloadable(url):
    """Determines if URL is a downloadable resource"""
    content_type = get_content_type(url)
    if is_text(url, content_type):
        return False
    if 'html' in content_type.lower():
        return False
    return True


def is_text(url, content_type=None):
    """Determines if a URL points to text"""
    # Allow user to skip step if content type already retrevied
    if content_type is None:
        content_type = get_content_type(url)
    # some text files have no content type header
    if content_type is None or "text" in content_type:
        return True
    return False


def download_file(url, out_name):
    """Downloads a file ot the given out_name"""
    r = _requests.get(url, allow_redirects=True)
    open(out_name, 'wb').write(r.content)


def save_text(url, out_name):
    """Save text to given filename to out_name"""
    r = _requests.get(url)
    open(out_name, 'w').write(r.text)


def is_ftp(url):
    """Determine if a url is over ftp protocol"""
    return _urllib.parse.urlparse(url).scheme == 'ftp'


def download_ftp(url, out_name):
    """Download a file from an ftp server to out_name"""
    # Parse the FTP url
    parsed = _urllib.parse.urlparse(url)
    server = parsed.netloc
    dl_path = parsed.path

    # Download the file
    ftp = _ftplib.FTP(server)
    ftp.login()
    ftp.retrbinary("RETR {}".format(dl_path), open(out_name, 'wb').write)
    ftp.quit()

def download(url, out_name=None, redownload=False):
    """
    Determiens the proper protocol to download a file from a URL.
    Will save the file to `out_name` and will by default skip if the output
    file already exists.

    :param url: The URL of the file to download
    :param out_name: The location to save the file to. If None, will parse the URL and save to cwd.
    :param redownload: Boolean, if False, will not download the file if `out_name` already exists.
        If True, will download the file again even if it exists.

    :return: None
    """

    if out_name is None:
        # Take the final element of the URL as filename if no out_name passed.
        out_name = url.split('/')[-1]
        file_name = out_name
    else:
        #Grab the base filename
        file_name = _os.path.basename(out_name)
        # Make sure the output directory exists
        out_dir = _os.path.dirname(out_name)
        if not _os.path.exists(out_dir):
            _os.path.makedirs(out_dir, exist_ok=True)

    # Only redownload an already existing file if user explicitly states
    if _os.path.exists(out_name) and not redownload:
        print('File {} exits. Skipping...'.format(file_name))
        return None

    # Use FTP for ftp transfers
    if is_ftp(url):
        print('Getting {} from ftp server'.format(file_name))
        download_ftp(url, out_name)
        print('Done')
    # Download downloadable files
    elif is_downloadable(url):
        print('Downloading {}'.format(file_name))
        download_file(url, out_name)
        print('Done')
    # Save text
    elif is_text(url):
        print('Saving {}'.format(file_name))
        save_text(url, out_name)
        print('Done')
    # Skip non-conforming files and print to screen.
    else:
        print(file_name, ": Not a downloadable file or text... ")
        print('Skipping....')

