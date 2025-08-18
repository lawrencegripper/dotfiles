#!/usr/bin/env python3
"""
Test script for the libvirt extension to verify it can connect and list VMs
"""

import subprocess
import sys

def test_virsh_connection():
    """Test if virsh can connect and list VMs"""
    try:
        print("Testing virsh connection...")
        result = subprocess.run(['virsh', 'list', '--all'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully connected to libvirt")
            print("Output:")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to connect to libvirt")
            print("Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout connecting to libvirt")
        return False
    except FileNotFoundError:
        print("❌ virsh command not found - please install libvirt-clients")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_virt_manager():
    """Test if virt-manager is available"""
    try:
        print("\nTesting virt-manager availability...")
        result = subprocess.run(['which', 'virt-manager'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ virt-manager found at:", result.stdout.strip())
            return True
        else:
            print("❌ virt-manager not found - please install virt-manager")
            return False
            
    except Exception as e:
        print(f"❌ Error checking virt-manager: {e}")
        return False

if __name__ == "__main__":
    print("Libvirt Extension Test")
    print("=" * 30)
    
    virsh_ok = test_virsh_connection()
    virt_manager_ok = test_virt_manager()
    
    print("\n" + "=" * 30)
    if virsh_ok and virt_manager_ok:
        print("✅ All tests passed! The extension should work properly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
