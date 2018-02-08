#!/usr/bin/python3

"""
 kernelstub
 The automatic manager for using the Linux Kernel EFI Stub to boot

 Copyright 2017-2018 Ian Santopietro <isantop@gmail.com>

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

Please see the provided LICENSE.txt file for additional distribution/copyright
terms.
"""

import subprocess, logging

class NVRAM():

    os_entry_index = -1
    os_label = ""
    nvram = []
    order_num = "0000"

    def __init__(self, name, version):
        self.log = logging.getLogger('kernelstub.NVRAM')
        self.log.debug('Logging set up')
        self.log.debug('loaded kernelstub.NVRAM')

        self.os_label = "%s %s" % (name, version)
        self.update()

    def update(self):
        self.nvram = self.get_nvram()
        self.find_os_entry(self.nvram, self.os_label)
        self.order_num = str(self.nvram[self.os_entry_index])[4:8]

    def get_nvram(self):
        command = [
            '/usr/bin/sudo',
            'efibootmgr'
        ]
        nvram = subprocess.check_output(command).decode('UTF-8').split('\n')
        return nvram

    def find_os_entry(self, nvram, os_label):
        self.os_entry_index = -1
        find_index = self.os_entry_index
        for entry in nvram:
            find_index = find_index + 1
            if os_label in entry:
                self.os_entry_index = find_index
                return find_index


    def add_entry(self, this_os, this_drive, kernel_opts):
        device = '/dev/%s' % this_drive.name
        esp_num = this_drive.esp_num
        entry_label = '%s-%s' % (this_os.name, this_os.version)
        entry_linux = '\\EFI\\%s-%s\\vmlinuz.efi' % (this_os.name, this_drive.root_uuid)
        root_uuid = this_drive.root_uuid
        entry_initrd = 'EFI/%s-%s/initrd.img' % (this_os.name, this_drive.root_uuid)
        self.log.debug('kernel opts: %s' % kernel_opts)

        command = [
            '/usr/bin/sudo',
            'efibootmgr',
            '-c',
            '-d', device,
            '-p', esp_num,
            '-L', '%s' % entry_label,
            '-l', entry_linux,
            '-u',
            '"initrd=%s' % entry_initrd,
            '%s"' % kernel_opts
        ]
        self.log.debug('Command is: %s' % command)
        subprocess.run(command)
        self.update()

    def delete_boot_entry(self, index):
        command = ['/usr/bin/sudo',
                   'efibootmgr',
                   '-B',
                   '-b', str(index)]
        subprocess.run(command)
        self.update()
