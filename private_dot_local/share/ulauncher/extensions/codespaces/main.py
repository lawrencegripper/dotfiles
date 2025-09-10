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
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from cachetools import cached, LRUCache, TTLCache


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
    branch: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'Codespace':
        _gitStatus = GitStatus.from_dict(obj.get("gitStatus"))
        _lastUsedAt = str(obj.get("lastUsedAt"))
        _name = str(obj.get("name"))
        _repository = str(obj.get("repository"))
        _branch = str(obj.get("branch"))
        return Codespace(_gitStatus, _lastUsedAt, _name, _repository)

@cached(cache=TTLCache(maxsize=10, ttl=5)) # cache for 5 seconds
def get_codespaces() -> List[Codespace]:
    command: str = "/home/linuxbrew/.linuxbrew/bin/gh codespace list --json name,gitStatus,lastUsedAt,repository,branch"
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
        query = event.get_argument() or ""
        
        try:
            codespaces = get_codespaces()
            
            # Filter codespaces based on query
            filtered_codespaces = []
            if query:
                for c in codespaces:
                    # Search in repository name, codespace name, and branch name
                    repo_name = c.repository.replace("github/", "")
                    if (query.lower() in repo_name.lower() or query.lower() in c.branch.lower()):
                        filtered_codespaces.append(c)
            else:
                filtered_codespaces = codespaces
            
            if not filtered_codespaces:
                items.append(ExtensionResultItem(
                    icon='images/codespace.png',
                    name='No codespaces found',
                    description='No codespaces match your search or no codespaces available',
                    on_enter=DoNothingAction()
                ))
            else:
                for c in filtered_codespaces:
                    has_uncommitted_changes = '📝' if c.gitStatus.hasUncommittedChanges else ' '
                    items.append(ExtensionResultItem(icon='images/codespace.png',
                                                     name=f'{c.repository.replace("github/", "")} {has_uncommitted_changes}',
                                                     description=f'{c.name} {c.gitStatus.ref}',
                                                     on_enter=RunScriptAction(f'/home/lawrencegripper/.dotfiles_bin/codespace-launch "{c.name}"'))
                    )
                    
        except Exception as e:
            items.append(ExtensionResultItem(
                icon='images/codespace.png',
                name='Error accessing codespaces',
                description=f'Failed to get codespace list: {str(e)}',
                on_enter=DoNothingAction()
            ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    CodespacesExtension().run()
