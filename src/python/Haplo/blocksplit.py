#!/illumina/development/haplocompare/hc-virtualenv/bin/python
# coding=utf-8
#
# Copyright (c) 2010-2015 Illumina, Inc.
# All rights reserved.
#
# This file is distributed under the simplified BSD license.
# The full text can be found here (and in LICENSE.txt in the root folder of
# this distribution):
#
# https://github.com/Illumina/licenses/blob/master/Simplified-BSD-License.txt
#
# 3/9/2015
#
# Author:
#
# Peter Krusche <pkrusche@illumina.com>
#

import os
import logging
import subprocess
import tempfile
import time


def blocksplitWrapper(location_str, args):
    starttime = time.time()
    tf = tempfile.NamedTemporaryFile(delete=False,
                                     dir=args.scratch_prefix,
                                     prefix="result.%s" % location_str,
                                     suffix=".chunks.bed")
    tf.close()

    to_run = "blocksplit %s %s -l %s -o %s --window %i --nblocks %i -f %i" % \
             (args.vcf1.replace(" ", "\\ "),
              args.vcf2.replace(" ", "\\ "),
              location_str,
              tf.name,
              args.window*2,
              args.pieces,
              0 if args.usefiltered or args.usefiltered_truth else 1)

    tfe = tempfile.NamedTemporaryFile(delete=False,
                                      dir=args.scratch_prefix,
                                      prefix="stderr",
                                      suffix=".log")
    tfo = tempfile.NamedTemporaryFile(delete=False,
                                      dir=args.scratch_prefix,
                                      prefix="stdout",
                                      suffix=".log")
    try:
        logging.info("Running '%s'" % to_run)
        subprocess.check_call(to_run, shell=True, stdout=tfo, stderr=tfe)
    finally:
        tfo.close()
        tfe.close()
        with open(tfo.name) as f:
            for l in f:
                logging.info(l.replace("\n", ""))
        os.unlink(tfo.name)
        with open(tfe.name) as f:
            for l in f:
                logging.warn(l.replace("\n", ""))
        os.unlink(tfe.name)

    elapsed = time.time() - starttime
    logging.info("blocksplit for %s -- time taken %.2f" % (location_str, elapsed))
    return tf.name