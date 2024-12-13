import argparse
import sys
import textwrap

from pathlib import Path
import re
import datetime

import chromagnon.SNSSParse
import chromagnon.sessionParse


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f'error: {message}', file=sys.stderr, flush=True)
        self.print_help()
        sys.exit(2)
        pass


def main():
    Parser = CustomArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
            [Chromagnon Chrome Session Parser]
            
            [Input File]
                The input file of this program is the Chrome Session File.
                It is encoded and the usual names are "Current Session" and
                "Session_..." whereas the underscore is followed with numerical 
                values.
            
            [Output Format]
                Current output is raw ordering of Session data. Other formats to come.
        ''')
    )

    # These options and formats will come at a later time. Currently, the sections are
    # hard coded so these formats don't won't work.

    # parser.add_argument('-f', '-format', action='store', default='classical',
    #                    choices=['csv','column','classical','json'],
    #                    help='Choose format for output formatting (csv, column, clasical, json)')
    # parser.add_argument('-d', '-delimiter', action='store',
    #                    help='Specify a delimiter for use in output formatting')
    Parser.add_argument('Filename', help='Path to Session file', type=str, nargs="?", default=None)
    tArgs = Parser.parse_args()

    if tArgs.Filename is None:
        tArgs.Filename = input("[Session File Path] ")
    tFilePath = Path(tArgs.Filename.strip("\""))
    tFileName = tFilePath.stem

    # Getting Data
    snss = chromagnon.SNSSParse.parse(tFilePath)

    # Parse Retrived data
    sessionCommand = chromagnon.sessionParse.parse(snss)

    # Print data based on SNSS Commands
    output = []

    # Parse timestamp from file name
    try:
        tMatch = re.search(r'\d+', tFileName)

        if tMatch:
            timestamp = int(tMatch.group())
            epoch_start = datetime.datetime(1601, 1, 1)
            delta = datetime.timedelta(microseconds=int(timestamp))
            human_readable_time = epoch_start + delta
        print(f"File Name: {tFileName}")
        print(f"Timestamp: {timestamp}")
        print(f"Human Readable Time: {human_readable_time} UTC")

    except Exception as e:
        print(e)

    tDict_TabID_Urls = {}

    for iCommand in sessionCommand:
        if isinstance(iCommand, chromagnon.sessionParse.CommandUpdateTabNavigation):
            tDict_TabID_Urls.setdefault(iCommand.tabId, [])
            tDict_TabID_Urls[iCommand.tabId].append(iCommand.url)

    tHTML_Bookmark = open(f"{tFilePath.parent / tFileName}.html", "w")
    tHTML_Bookmark.write("""
    <!DOCTYPE NETSCAPE-Bookmark-file-1>
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
    <!-- This is an automatically generated file.
    It will be read and overwritten.
    Do Not Edit! -->
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
    <DL><p>
    """)
    for iUrls in tDict_TabID_Urls.values():
        iLastUrl = iUrls[-1]
        tHTML_Bookmark.write(f'<DT><A HREF="{iLastUrl}">{iLastUrl}</A>\n')

    tHTML_Bookmark.write('</DT><p>')
    tHTML_Bookmark.close()

    # Handle table printing
    pass


if __name__ == "__main__":
    main()
