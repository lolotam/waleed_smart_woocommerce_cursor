import hashlib
import socket
import uuid
import platform
import psutil
import win32com.client
import win32api
import re

def get_mac_address():
    """Get the MAC address of the first network interface"""
    try:
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return mac
    except Exception:
        return "00:00:00:00:00:00"

def get_cpu_id():
    """Get CPU information to identify the machine"""
    try:
        # Use WMI to get CPU information
        wmi = win32com.client.GetObject("winmgmts:")
        cpu_info = ""
        for cpu in wmi.InstancesOf("Win32_Processor"):
            cpu_info += f"{cpu.ProcessorId.strip()}"
        
        if not cpu_info:
            # Fallback to processor name if ID not available
            cpu_info = platform.processor()
        
        return cpu_info
    except Exception:
        # Fallback to platform processor info
        return platform.processor()

def get_disk_serial():
    """Get the disk serial number"""
    try:
        # Get the system drive (usually C:)
        system_drive = win32api.GetSystemDirectory()[:2]
        
        # Get disk information
        wmi = win32com.client.GetObject("winmgmts:")
        for disk in wmi.InstancesOf("Win32_DiskDrive"):
            disk_info = str(disk.SerialNumber).strip()
            if disk_info:
                return disk_info
        
        return "UNKNOWN_DISK"
    except Exception:
        return "UNKNOWN_DISK"

def get_hostname():
    """Get the hostname of the machine"""
    try:
        return socket.gethostname()
    except Exception:
        return "UNKNOWN_HOST"

def get_machine_fingerprint():
    """
    Combine multiple machine identifiers to create a unique fingerprint
    This makes it harder to bypass the hardware lock
    """
    # Collect all identifiers
    mac = get_mac_address()
    cpu = get_cpu_id()
    hostname = get_hostname()
    disk = get_disk_serial()
    
    # Additional identifiers to make fingerprint more unique
    os_info = platform.platform()
    memory = str(psutil.virtual_memory().total)
    
    # Combine all identifiers
    fingerprint_data = f"{mac}|{cpu}|{hostname}|{disk}|{os_info}|{memory}"
    
    # Hash the combined data to create the fingerprint
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    return fingerprint

def get_simplified_fingerprint():
    """Get a simplified machine fingerprint (less secure but more portable)"""
    # Use just the essential identifiers
    mac = get_mac_address()
    hostname = get_hostname()
    os_info = platform.platform()
    
    # Combine and hash
    data = f"{mac}|{hostname}|{os_info}"
    return hashlib.md5(data.encode()).hexdigest()

if __name__ == "__main__":
    # When run directly, print out machine identifiers for diagnostics
    print(f"MAC Address: {get_mac_address()}")
    print(f"CPU ID: {get_cpu_id()}")
    print(f"Hostname: {get_hostname()}")
    print(f"Disk Serial: {get_disk_serial()}")
    print(f"Machine Fingerprint: {get_machine_fingerprint()}")
    print(f"Simplified Fingerprint: {get_simplified_fingerprint()}") 