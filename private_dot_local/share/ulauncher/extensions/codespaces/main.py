from time import sleep
import subprocess
from pathlib import Path
from typing import Any
from dataclasses import dataclass
import json
from typing import List
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
# from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction


@dataclass
class GitStatus:
    ahead: int
    behind: int
    hasUncommittedChanges: bool
    hasUnpushedChanges: bool
    ref: str

    @staticmethod
    def from_dict(obj: Any) -> 'GitStatus':
        _ahead = int(obj.get("ahead"))
        _behind = int(obj.get("behind"))
        _hasUncommittedChanges = bool(obj.get("hasUncommittedChanges"))
        _hasUnpushedChanges = bool(obj.get("hasUnpushedChanges"))
        _ref = str(obj.get("ref"))
        return GitStatus(_ahead, _behind, _hasUncommittedChanges, _hasUnpushedChanges, _ref)

@dataclass
class Codespace:
    gitStatus: GitStatus
    lastUsedAt: str
    name: str
    repository: str

    @staticmethod
    def from_dict(obj: Any) -> 'Codespace':
        _gitStatus = GitStatus.from_dict(obj.get("gitStatus"))
        _lastUsedAt = str(obj.get("lastUsedAt"))
        _name = str(obj.get("name"))
        _repository = str(obj.get("repository"))
        return Codespace(_gitStatus, _lastUsedAt, _name, _repository)

def get_codespaces() -> List[Codespace]:
    command: str = "/home/linuxbrew/.linuxbrew/bin/gh codespace list --json name,gitStatus,lastUsedAt,repository"
    response = subprocess.run(command.split(' '), capture_output=True)
    codespaces: List[dict] = json.loads(response.stdout)

    codespace_list: List[Codespace] = []
    for c in codespaces:
        codespace_list.append(Codespace.from_dict(c))
    codespace_list.reverse()
    return codespace_list

class CodespacesExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        for c in get_codespaces():
            has_uncommitted_changes = '💡' if c.gitStatus.hasUncommittedChanges else ' '
            items.append(ExtensionResultItem(icon='images/codespace.png',
                                             name=f'{c.repository} {c.gitStatus.ref} {has_uncommitted_changes}',
                                             description=f'{c.name}',
                                             on_enter=DoNothingAction()))

        return RenderResultListAction(items)

if __name__ == '__main__':
    CodespacesExtension().run()
