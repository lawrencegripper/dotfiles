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
md_name = 'GreenClip'
md_description = 'Clipboard history for greenclip'
md_url = 'https://github.com/lawrencegripper/dotfiles'
md_lib_dependencies = []


def get_clipboard_history() -> List[str]:
    command: str = "greenclip print"
    response = subprocess.run(command.split(' '), capture_output=True)
    return response.stdout.decode('utf-8').splitlines()

class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<text in clipboard>",
                                     defaultTrigger='cl ',
                                     supportsFuzzyMatching=True)
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/clipboard.svg"]

    def handleTriggerQuery(self, query):
        ranked_items: List[RankItem] = []
        stripped = query.string.strip()

        for clip in get_clipboard_history():
            score = SequenceMatcher(None, stripped, clip).ratio()
            ranked_items.append(
                RankItem(
                    StandardItem(
                        id=md_id,
                        text=clip,
                        iconUrls=self.iconUrls,
                        actions=[
                            Action("paste", "Paste", lambda c=clip: setClipboardTextAndPaste(c)),
                            Action("set", "Set Clipboard", lambda c=clip: setClipboardText(c)),
                            Action("clearhistory", "Clear History", lambda: runTerminal(f'greenclip clear', close_on_exit=True)),
                        ]
                    ),
                    score
                )
            )
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        for i in map(lambda x: x.item, ranked_items):
            query.add(i)