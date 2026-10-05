#!/usr/bin/env python3

import socket
import threading
import argparse
import sys
import json
import csv
from datetime import datetime
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

COMMON_SERVICES = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
    443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL',
    3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Alt', 8888: 'Custom'
}

class PortScanner:
    def __init__(self, target, ports, threads=50, timeout=1):
        self.target = target
        self.ports = ports
        self.threads = threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        
    def get_service(self, port):
        return COMMON_SERVICES.get(port, 'Unknown')
    
    def scan_port(self, port, pbar):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                service = self.get_service(port)
                with self.lock:
                    self.open_ports.append((port, service))
                    pbar.write(f"{Fore.GREEN}[+] Port {port:5d} - {service}{Style.RESET_ALL}")
        except:
            pass
        finally:
            pbar.update(1)
    
    def run(self):
        print(f"{Fore.CYAN}[*] Target: {self.target}")
        print(f"{Fore.CYAN}[*] Ports: {len(self.ports)}")
        print(f"{Fore.CYAN}[*] Threads: {self.threads}\n")
        
        threads = []
        
        with tqdm(total=len(self.ports), desc="Scanning", unit="port", colour='green') as pbar:
            for port in self.ports:
                while threading.active_count() > self.threads + 2:
                    pass
                
                t = threading.Thread(target=self.scan_port, args=(port, pbar))
                t.daemon = True
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()
        
        return self.open_ports
    
    def save_results(self, filename, format='json'):
        if not self.open_ports:
            print(f"{Fore.YELLOW}[!] No open ports found")
            return
        
        if format == 'json':
            data = {
                'target': self.target,
                'timestamp': datetime.now().isoformat(),
                'open_ports': [{'port': p, 'service': s} for p, s in self.open_ports]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        
        elif format == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Port', 'Service', 'Timestamp'])
                for port, service in self.open_ports:
                    writer.writerow([port, service, datetime.now().isoformat()])
        
        print(f"{Fore.GREEN}[+] Results saved to {filename}")

def parse_ports(port_str):
    ports = []
    for part in port_str.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            except:
                print(f"{Fore.RED}[ERROR] Invalid port range: {part}")
                sys.exit(1)
        else:
            try:
                ports.append(int(part))
            except:
                print(f"{Fore.RED}[ERROR] Invalid port: {part}")
                sys.exit(1)
    return sorted(list(set(ports)))

def main():
    parser = argparse.ArgumentParser(description='Advanced Port Scanner')
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('-p', '--ports', default='1-1000', help='Ports to scan (default: 1-1000)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=float, default=1, help='Socket timeout (default: 1s)')
    parser.add_argument('-o', '--output', help='Save results to file')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    try:
        ports = parse_ports(args.ports)
        if not ports:
            print(f"{Fore.RED}[ERROR] No valid ports")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Port parsing failed: {e}")
        sys.exit(1)
    
    try:
        scanner = PortScanner(args.target, ports, args.threads, args.timeout)
        open_ports = scanner.run()
        
        print(f"\n{Fore.CYAN}[*] Scan complete!")
        print(f"{Fore.GREEN}[+] Found {len(open_ports)} open port(s)\n")
        
        if open_ports:
            print(f"{Fore.CYAN}Port    Service")
            print(f"{Fore.CYAN}-" * 30)
            for port, service in open_ports:
                print(f"{Fore.GREEN}{port:5d}   {service}")
            print()
        
        if args.output:
            scanner.save_results(args.output, args.format)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
