#!/usr/bin/env python3
import os
import sys
import binascii
import getopt

__author__ = 'kayws426'
__version__ = 'v0.1'


class file_info:
    """
    the file_info class
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.check_sum_hex = None

    def read_crc32(self):
        """
        compute CRC32 checksum

        :return: CRC32 result
        """
        if self.check_sum_hex is None:
            if self.file_name == "-" or self.file_name == "<stdin>":
                fp = sys.stdin
                file_data = bytearray(fp.read(), 'utf-8')
            else:
                fp = open(self.file_name, 'rb')
                file_data = fp.read()
                fp.close()

            check_sum_int = binascii.crc32(file_data) & 0xFFFFFFFF

            self.check_sum_hex = "%08X" % check_sum_int

        return self.check_sum_hex


class crc32sum_app:
    """
    the crc32sum_app class
    """
    def __init__(self, app_name):
        self.app_name = app_name
        self.read_fail_count = 0
        self.checksum_not_match_count = 0

    def to_checksum_format(self, file_names="<stdin>"):
        """
        print CRC32 as checksum format

        :param file_names:
        :return:
        """
        self.read_fail_count = 0

        for file_name in file_names:
            fi = file_info(file_name)
            try:
                crc32_str = fi.read_crc32()
                sys.stdout.write("%s %s\n" %
                                 (crc32_str, fi.file_name.replace('\\', '/')))

            except Exception as e:
                result = "FAILED open or read"
                sys.stderr.write("%s: %s: %s (%s).\n" %
                                 (self.app_name, file_name, result, e))
                self.read_fail_count += 1

        return self.read_fail_count

    def check(self, check_file_name, out_file_name="<stdout>"):
        if out_file_name == "<stdout>":
            out_file = sys.stdout
        else:
            out_file = open(out_file_name, 'w');

        try:
            if check_file_name == "-" or check_file_name == "<stdin>":
                check_file = sys.stdin
            else:
                check_file = open(check_file_name, 'rb');
        except:
            sys.stderr.write("%s: %s: No such file or directory\n" %
                             (self.app_name, check_file_name))
            return 1

        self.read_fail_count = 0
        self.checksum_not_match_count = 0

        for line in check_file.readlines():
            #line_info = line.split()
            try:
                try:
                    enc = 'utf-8'
                    line = line.decode(enc)
                except:
                    enc = 'cp949'
                    line = line.decode(enc)
            except:
                enc = None
                pass
            line_info = [line[0:8], line[8:]]
            file_checksum = line_info[0].strip()
            file_name = line_info[1].strip().strip('*')
            file_name_encoded = file_name
            if os.environ.get('SHLVL') != None:
                file_name_encoded = file_name.encode('utf-8')
            result = ""
            try:
                fi = file_info(file_name)
                check_sum = fi.read_crc32()

                if check_sum.upper() == file_checksum.upper():
                    result = "OK"
                else:
                    result = "FAILED"
                    self.checksum_not_match_count += 1
            except:
                sys.stderr.write("%s: %s: No such file or directory\n" %
                                 (self.app_name, file_name_encoded))
                sys.stderr.flush()
                result = "FAILED open or read"
                self.read_fail_count += 1

            out_file.write("%s: %s\n" % (file_name_encoded, result))
            out_file.flush()

        if self.read_fail_count > 0:
            sys.stderr.write("%s: WARNING: %d listed file could not be read\n"
                             % (self.app_name, self.read_fail_count))
        if self.checksum_not_match_count > 0:
            sys.stderr.write("%s: WARNING: %d computed checksums did NOT match\n"
                             % (self.app_name, self.checksum_not_match_count))

        return (self.read_fail_count + self.checksum_not_match_count)

    def run(self, file_names, check_mode, check_file):
        if check_mode:
            return self.check(check_file)
        else:
            return self.to_checksum_format(file_names)


def print_help(app_name):
    """
    print help
    :return:
    """
    sys.stdout.write("Usage: " + app_name + " [OPTION]... [FILE]...\n")
    sys.stdout.write("Print or check CRC32 (32-bit) checksums.\n")
    sys.stdout.write("\n")
    sys.stdout.write("With no FILE, or when FILE is -, read standard input.\n")
    sys.stdout.write("\n")
    sys.stdout.write("  -c, --check      read CRC32 sums from the FILEs and check them\n")


def main():
    app_name = "crc32sum"
    optlist, args = getopt.getopt(sys.argv[1:], "c:h", ["check=", "help"])

    p_input_files = []
    p_check_mode = False
    p_check_file = None

    for opt, val in optlist:
        if opt in ["-c", "--check"]:
            p_check_file = val
            p_check_mode = True
        elif opt in ["-h", "--help"]:
            print_help(app_name)
            return 1
        else:
            sys.stdout.write("%s: unknown option : %s / %s\n" % (app_name, opt, val))
            sys.stdout.write("Try '%s --help' for more infomation\n" % (app_name))
            return 1

    if args is not None:
        p_input_files.extend(args)

    if len(p_input_files) == 0 and not p_check_mode:
        p_input_files.append("<stdin>")

    app = crc32sum_app(app_name)
    ret = app.run(file_names = p_input_files, check_mode = p_check_mode, check_file = p_check_file)
    return ret


if __name__ == "__main__":
    ret = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(ret)
