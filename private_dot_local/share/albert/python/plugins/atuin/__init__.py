"""
Inline codespace launcher.
"""

from albert import *
import subprocess
from pathlib import Path
from typing import List
from difflib import SequenceMatcher

md_iid = '2.0'
md_version = '1.0'
md_name = 'Atuin'
md_description = 'Search and run command from atuin history'
md_url = 'https://github.com/lawrencegripper/dotfiles'
md_lib_dependencies = []


def get_command_history(query: str) -> List[str]:
    command: str = f'atuin search --limit 10 --cmd-only "{query}"'
    response = subprocess.run(command, executable="/bin/bash", capture_output=True, shell=True)
    response = response.stdout.decode('utf-8').splitlines()
    response.reverse
    return response


def score(query: TriggerQuery, item: Item) -> float:
    return SequenceMatcher(None, item.text.lower(), query.string.lower()).ratio()

class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<command from history>",
                                     defaultTrigger='ch ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/bash.svg"]

    def handleTriggerQuery(self, query):
        items: List[Item] = []
        stripped = query.string.strip()

        for command in get_command_history(stripped):
            items.append(
                StandardItem(
                        id=md_id,
                        text=command,
                        iconUrls=self.iconUrls,
                        actions=[
                            Action("ssh", "SSH", lambda n=command: runTerminal(f'gh codespace ssh --codespace {n}')),
                            Action("paste", "Paste", lambda c=command: setClipboardTextAndPaste(c)),
                            Action("set", "Set Clipboard", lambda c=command: setClipboardText(c)),
                        ]
                )
            )
        items.sort(key=lambda i: score(query, i), reverse=True)
        for i in items:
            query.add(i)