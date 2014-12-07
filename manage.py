#!/usr/bin/env python
import os
import sys
import xmascontroller

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xmas.settings")

    from django.core.management import execute_from_command_line

    print "starting up xmascontroller"
    args = list(sys.argv)
    if ("--noserial" in args):
        args.remove("--noserial")
        xmascontroller.startup(noSerial=True)
    else:
        if not ("--noreload" in args):
            print >> sys.stderr, "please use --noreload after runserver"
            sys.exit(-1)
        xmascontroller.startup(noSerial=False)
    print "finished starting up xmascontroller"

    execute_from_command_line(args)
