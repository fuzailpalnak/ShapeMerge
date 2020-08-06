from sys import stdout


class Printer:
    @staticmethod
    def print(data):
        stdout.write("\r\033[1;37m>>\x1b[K" + data.__str__())
        stdout.flush()

    @staticmethod
    def print_new_line(data):
        stdout.write("\n")
        stdout.write("\r\033[1;37m>>\x1b[K" + data.__str__())
        stdout.flush()
