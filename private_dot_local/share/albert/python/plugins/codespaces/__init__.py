"""
Inline codespace launcher.
"""

from albert import *
import subprocess
from pathlib import Path
from time import sleep
from typing import Any
from dataclasses import dataclass
import json
from typing import List

md_iid = '2.0'
md_version = '1.0'
md_name = 'Codespaces'
md_description = 'Find and lauch your codespaces'
md_url = 'https://github.com/lawrencegripper/dotfiles'
md_lib_dependencies = []


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
    command: str = "gh codespace list --json name,gitStatus,lastUsedAt,repository"
    response = subprocess.run(command.split(' '), capture_output=True)
    codespaces: List[dict] = json.loads(response.stdout)

    codespace_list: List[Codespace] = []
    for c in codespaces:
        codespace_list.append(Codespace.from_dict(c))
    return codespace_list

class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     synopsis="<query>",
                                     defaultTrigger='cs ')
        PluginInstance.__init__(self, extensions=[self])
        self.iconUrls = [f"file:{Path(__file__).parent}/codespace.svg"]

    def handleTriggerQuery(self, query):

        stripped = query.string.strip()
        if stripped:

            # dont flood
            for number in range(25):
                sleep(0.01)
                if not query.isValid:
                    return

            for c in get_codespaces():
                query.add(
                    StandardItem(
                        id=md_id,
                        text=c.repository,
                        subtext=c.name,
                        iconUrls=self.iconUrls,
                        actions=[Action("open", "Open link", lambda u=c.name: runDetachedProcess('codespace-launch', u))]
                    )
                )