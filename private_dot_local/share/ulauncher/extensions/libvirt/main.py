from time import sleep
import subprocess
from pathlib import Path
from typing import Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET
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


@dataclass
class VirtualMachine:
    name: str
    state: str
    uuid: str
    autostart: bool

    @staticmethod
    def from_virsh_list(line: str) -> 'VirtualMachine':
        # Parse virsh list output line format: "ID Name State"
        parts = line.strip().split()
        if len(parts) >= 3:
            vm_id = parts[0] if parts[0] != '-' else None
            name = parts[1]
            state = ' '.join(parts[2:])
            return VirtualMachine(name, state, '', False)
        return VirtualMachine('', '', '', False)  # Return empty VM instead of None

def get_virtual_machines() -> List[VirtualMachine]:
    """Get list of all VMs from libvirt using virsh"""
    vms = []
    
    try:
        # Get all VMs (running and stopped)
        command = ["virsh", "--connect", "qemu:///system", "list", "--all"]
        response = subprocess.run(command, capture_output=True, text=True)
        
        if response.returncode != 0:
            return []
        
        lines = response.stdout.strip().split('\n')
        # Skip header lines
        for line in lines[2:]:
            if line.strip() and not line.startswith('---'):
                vm = VirtualMachine.from_virsh_list(line)
                if vm and vm.name:  # Only add VMs with valid names
                    vms.append(vm)
                
    except Exception as e:
        print(f"Error getting VMs: {e}")
    
    return vms

def get_state_emoji(state: str) -> str:
    """Return emoji based on VM state"""
    state_lower = state.lower()
    if 'running' in state_lower:
        return '🟢'
    elif 'shut off' in state_lower or 'stopped' in state_lower:
        return '🔴'
    elif 'paused' in state_lower:
        return '🟡'
    elif 'suspended' in state_lower:
        return '🟡'
    else:
        return '⚪'

def open_vm_in_virt_manager(vm_name: str) -> str:
    # Try to open the specific VM, fallback to just opening virt-manager
    return (
        f'bash -c "'
        f"virsh --connect qemu:///system start '{vm_name}'; "
        f"virt-manager --connect qemu:///system --show-domain-console '{vm_name}' 2>/dev/null || "
        f"virt-manager --connect qemu:///system"
        f'"'
    )

class LibvirtExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        query = event.get_argument() or ""
        
        try:
            vms = get_virtual_machines()
            
            # Filter VMs based on query
            filtered_vms = []
            if query:
                for vm in vms:
                    if query.lower() in vm.name.lower():
                        filtered_vms.append(vm)
            else:
                filtered_vms = vms
            
            if not filtered_vms:
                items.append(ExtensionResultItem(
                    icon='images/vm.png',
                    name='No VMs found',
                    description='No virtual machines match your search or libvirt is not available',
                    on_enter=DoNothingAction()
                ))
            else:
                for vm in filtered_vms:
                    state_emoji = get_state_emoji(vm.state)
                    autostart_indicator = '🔄' if vm.autostart else ''
                    
                    items.append(ExtensionResultItem(
                        icon='images/vm.png',
                        name=f'{state_emoji} {vm.name} {autostart_indicator}',
                        description=f'State: {vm.state} • Click to open in virt-manager',
                        on_enter=RunScriptAction(open_vm_in_virt_manager(vm.name))
                    ))
                    
        except Exception as e:
            items.append(ExtensionResultItem(
                icon='images/vm.png',
                name='Error accessing libvirt',
                description=f'Failed to get VM list: {str(e)}',
                on_enter=DoNothingAction()
            ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    LibvirtExtension().run()
