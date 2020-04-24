# pylint: disable=C0111,R0903

"""Displays update information per repository for pacman.

Parameters:
    * pacman.sum: If you prefere displaying updates with a single digit (defaults to "False")

Requires the following executables:
    * fakeroot
    * pacman
"""

import os
import threading

import bumblebee.util
import bumblebee.input
import bumblebee.output
import bumblebee.engine

#list of repositories.
#the last one should always be other
repos = ["core", "extra", "community", "multilib", "testing", "other"]

def get_pacman_info(widget, path):
    try:
        cmd = "{}/../../bin/pacman-updates".format(path)
        if not os.path.exists(cmd):
            cmd = "/usr/share/bumblebee-status/bin/pacman-update"
        result = bumblebee.util.execute(cmd)
    except:
        pass

    count = len(repos)*[0]

    for line in result.splitlines():
        if line.startswith(("http", "rsync")):
            for i in range(len(repos)-1):
                if "/" + repos[i] + "/" in line:
                    count[i] += 1
                    break
            else:
                result[-1] += 1

    for i in range(len(repos)):
        widget.set(repos[i], count[i])


class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.updates)
        )
        self._count = 0

    def updates(self, widget):
        if bumblebee.util.asbool(self.parameter("sum")):
            return str(sum(map(lambda x: widget.get(x, 0), repos)))
        return '/'.join(map(lambda x: str(widget.get(x, 0)), repos))

    def update(self, widgets):
        path = os.path.dirname(os.path.abspath(__file__))
        if self._count == 0:
            thread = threading.Thread(target=get_pacman_info, args=(widgets[0], path))
            thread.start()

        # TODO: improve this waiting mechanism a bit
        self._count += 1
        self._count = 0 if self._count > 300 else self._count

    def state(self, widget):
        weightedCount = sum(map(lambda x: (len(repos)-x[0]) * widget.get(x[1], 0), enumerate(repos)))

        if weightedCount < 10:
            return "good"

        return self.threshold_state(weightedCount, 100, 150)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
