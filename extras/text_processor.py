# -*- coding: utf-8 -*-
"""text_processor.py
A simple (pre-)processor for crec docs.

Created on Sun Feb 14 10:28:23 2016

@author: Eric Chen
"""
import os
import re


if __name__ == '__main__':
    errors = 0
    files = [
        filename for filename in os.listdir('.') if os.path.isfile(filename)]
    for filename in files:
        # Read the file.
        with open(filename, 'r') as f:
            doc = f.read()

        # Process the contents.
        if filename.endswith('htm'):
            base_filename = os.path.basename(filename).split('.')[0]+'.txt'
        else:
            # This simple parser only parses .htm files.
            continue
            # base_filename = os.path.basename(filename)
        saveas = os.path.join('./raw/', base_filename)
        if not os.path.exists(saveas):
            # re.DOTALL is important - it tells 'dot' (.) to match newline.
            findraw = re.compile(
                r'<body><pre>(?P<raw>.*)</pre></body>', re.DOTALL)
            try:
                # Check the file extension again.
                if not filename.endswith('htm'):
                    continue
                # Only extract the raw text, without the open & close
                # html tags.
                raw = findraw.search(doc).group('raw')
                # Remove all <bullet> strings.
                raw = re.sub(r'<bullet>', ' ', raw)

                with open(saveas, 'w') as save_f:
                    # Though inefficient, clean-up by re-parsing line-by-line.
                    for line in raw.splitlines():
                        line = line.strip()

                        # Check for lines we want to skip.
                        if line.startswith('[') and \
                                line.endswith(']'):
                            continue
                        elif line.startswith(
                                'From the Congressional Record Online'):
                            continue
                        elif line.startswith(
                                'ADDITIONAL STATEMENTS'):
                            continue
                        elif line.startswith(
                                '______'):
                            continue

                        # Replace some of the punctuation.
                        line = line.replace(".,!?-", "")

                        # Write the cleaned line to the file.
                        save_f.write(line)
                        save_f.write('\n')

            except BaseException, e:
                # Catch any errors and move on.
                errors += 1
                print 'Problem processing file %s. Error:' % filename
                print e
        else:
            print 'file %s already exists. skipping.' % saveas
