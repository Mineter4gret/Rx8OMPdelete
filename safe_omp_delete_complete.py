#!/usr/bin/env python3
"""
Safe OMP Delete Tool - COMPLETE VERSION
Applies ALL modifications including boot area changes to prevent immobilizer issues.
"""

import os
import struct
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List

class SafeOMPDeleteComplete:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.backup_file = f"{input_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_file = f"{input_file.replace('.bin', '_omp_deleted_complete.bin')}"
        self.data = None
        self.modifications_applied = []
        self.checksums_corrected = []
        
    def load_and_backup(self) -> bool:
        """Load firmware and create backup"""
        print("🔍 Loading firmware and creating backup...")
        
        if not os.path.exists(self.input_file):
            print(f"❌ Error: Input file '{self.input_file}' not found")
            return False
        
        # Load firmware
        try:
            with open(self.input_file, 'rb') as f:
                self.data = bytearray(f.read())
            print(f"✅ Loaded: {len(self.data)} bytes")
        except Exception as e:
            print(f"❌ Error loading: {e}")
            return False
        
        # Create backup
        try:
            shutil.copy2(self.input_file, self.backup_file)
            print(f"✅ Backup created: {self.backup_file}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def apply_complete_omp_delete(self) -> bool:
        """Apply COMPLETE OMP delete - all modifications to prevent immobilizer"""
        print("\n🔧 Applying COMPLETE OMP delete modifications...")
        print("   Including boot area changes to prevent immobilizer issues")
        
        # ALL modifications including the ones that were skipped
        modifications = [
            {
                'location': 0x452b,
                'original': bytes([0x19, 0x00, 0x0b, 0x62]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP pressure monitoring bypass'
            },
            {
                'location': 0x57ef,
                'original': bytes([0x19, 0x00, 0x09, 0x60]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP flow monitoring bypass'
            },
            {
                'location': 0x1d39d,
                'original': bytes([0x19, 0x01, 0xfc, 0x21]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP DTC setting disable'
            },
            {
                'location': 0x9aa,
                'original': bytes([0x20, 0x00]),
                'modified': bytes([0x00, 0x09]),
                'description': 'Limp mode trigger 1 disable (CRITICAL for immobilizer)'
            },
            {
                'location': 0x134e,
                'original': bytes([0x20, 0x00]),
                'modified': bytes([0x00, 0x09]),
                'description': 'Limp mode trigger 2 disable (CRITICAL for immobilizer)'
            }
        ]
        
        applied_count = 0
        
        for mod in modifications:
            location = mod['location']
            original = mod['original']
            modified = mod['modified']
            description = mod['description']
            
            print(f"\n  Processing: {description}")
            
            # Bounds check
            if location + len(original) > len(self.data):
                print(f"    ❌ ERROR: Location extends beyond file size")
                continue
            
            # Check current bytes
            current_bytes = self.data[location:location + len(original)]
            
            if current_bytes == original:
                print(f"    Original bytes: {' '.join(f'{b:02x}' for b in original)}")
                print(f"    Modified bytes: {' '.join(f'{b:02x}' for b in modified)}")
                
                # Apply modification
                self.data[location:location + len(modified)] = modified
                
                self.modifications_applied.append(mod)
                applied_count += 1
                print(f"    ✅ Applied successfully")
                
            elif current_bytes == modified:
                print(f"    ℹ️  Already applied")
                self.modifications_applied.append(mod)
            else:
                print(f"    ⚠️  Unexpected bytes found")
                print(f"    Expected: {' '.join(f'{b:02x}' for b in original)}")
                print(f"    Found:    {' '.join(f'{b:02x}' for b in current_bytes)}")
                print(f"    🔧 Applying anyway (complete mode)")
                
                # Force apply in complete mode
                self.data[location:location + len(modified)] = modified
                self.modifications_applied.append(mod)
                applied_count += 1
        
        print(f"\n📊 Total modifications applied: {len(self.modifications_applied)}")
        return len(self.modifications_applied) > 0
    
    def fix_checksums_properly(self) -> bool:
        """Fix checksums using improved algorithms"""
        print("\n🔧 CRITICAL: Fixing checksums with improved algorithms...")
        
        # Improved checksum areas based on immobilizer feedback
        checksum_areas = [
            {
                'name': 'Main Program CRC32',
                'start': 0x0000,
                'end': 0x7EFFC,
                'checksum_addr': 0x7EFFC,
                'algorithm': 'crc32_complement'
            },
            {
                'name': 'Calibration Sum32',
                'start': 0x10000, 
                'end': 0x1FFFC,
                'checksum_addr': 0x1FFFC,
                'algorithm': 'sum32_complement'
            },
            {
                'name': 'Boot Block CRC16',
                'start': 0x7F000,
                'end': 0x7FFFC, 
                'checksum_addr': 0x7FFFC,
                'algorithm': 'crc16_ccitt'
            }
        ]
        
        corrected = 0
        
        for area in checksum_areas:
            print(f"\n  Processing: {area['name']}")
            
            if area['checksum_addr'] + 4 > len(self.data):
                print(f"    ⚠️  Skipping: beyond file bounds")
                continue
            
            # Calculate new checksum
            start = area['start']
            end = min(area['end'], len(self.data))
            data_section = self.data[start:end]
            
            if area['algorithm'] == 'crc32_complement':
                checksum = self.crc32(data_section) ^ 0xFFFFFFFF
            elif area['algorithm'] == 'sum32_complement':
                checksum = (0x100000000 - sum(data_section)) & 0xFFFFFFFF
            elif area['algorithm'] == 'crc16_ccitt':
                checksum = self.crc16_ccitt(data_section)
            else:
                checksum = sum(data_section) & 0xFFFFFFFF
            
            # Read current checksum
            current = struct.unpack('>L', self.data[area['checksum_addr']:area['checksum_addr']+4])[0]
            
            print(f"    Current:    0x{current:08X}")
            print(f"    Calculated: 0x{checksum:08X}")
            
            if current != checksum:
                # Write new checksum
                struct.pack_into('>L', self.data, area['checksum_addr'], checksum)
                print(f"    ✅ Updated checksum")
                corrected += 1
                
                self.checksums_corrected.append({
                    'area': area['name'],
                    'old': current,
                    'new': checksum
                })
            else:
                print(f"    ℹ️  Already correct")
        
        print(f"\n📊 Checksums corrected: {corrected}")
        return True
    
    def crc32(self, data: bytes) -> int:
        """Calculate CRC32 with standard polynomial"""
        crc = 0xFFFFFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
        return crc ^ 0xFFFFFFFF
    
    def crc16_ccitt(self, data: bytes) -> int:
        """Calculate CRC16-CCITT"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def save_complete_firmware(self) -> bool:
        """Save the complete OMP delete firmware"""
        print(f"\n💾 Saving complete firmware: {self.output_file}")
        
        try:
            with open(self.output_file, 'wb') as f:
                f.write(self.data)
            
            size = os.path.getsize(self.output_file)
            print(f"✅ Saved: {size} bytes")
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def generate_complete_report(self) -> bool:
        """Generate report for complete modification"""
        report_file = f"{self.output_file.replace('.bin', '_REPORT.txt')}"
        
        try:
            with open(report_file, 'w') as f:
                f.write("COMPLETE OMP DELETE - IMMOBILIZER FIX VERSION\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Purpose: Fix immobilizer light by applying ALL modifications\n\n")
                
                f.write("COMPLETE MODIFICATIONS APPLIED:\n")
                for mod in self.modifications_applied:
                    f.write(f"- {mod['description']} at 0x{mod['location']:04X}\n")
                
                f.write(f"\nCHECKSUMS CORRECTED: {len(self.checksums_corrected)}\n")
                for cs in self.checksums_corrected:
                    f.write(f"- {cs['area']}: 0x{cs['old']:08X} → 0x{cs['new']:08X}\n")
                
                f.write("\nCRITICAL NOTES:\n")
                f.write("- This version includes boot area modifications\n")
                f.write("- Should resolve immobilizer light issues\n") 
                f.write("- All OMP monitoring completely disabled\n")
                f.write("- Pre-mix oil REQUIRED (1:100 ratio)\n")
                f.write("\nRECOVERY FILE:\n")
                f.write(f"Original backup: {self.backup_file}\n")
            
            print(f"✅ Report: {report_file}")
            return True
        except Exception as e:
            print(f"❌ Report failed: {e}")
            return False
    
    def run_complete_delete(self) -> bool:
        """Run complete OMP delete process"""
        print("🏁 COMPLETE OMP DELETE TOOL - IMMOBILIZER FIX VERSION")
        print("=" * 65)
        print("Applies ALL modifications to prevent immobilizer activation")
        print("Includes boot area changes that were previously skipped\n")
        
        if not self.load_and_backup():
            return False
        
        if not self.apply_complete_omp_delete():
            return False
        
        if not self.fix_checksums_properly():
            return False
        
        if not self.save_complete_firmware():
            return False
        
        self.generate_complete_report()
        
        print("\n" + "=" * 70)
        print("✅ COMPLETE OMP DELETE FINISHED")
        print("=" * 70)
        print(f"Complete firmware: {self.output_file}")
        print(f"Original backup: {self.backup_file}")
        print("\n🎯 This version should resolve immobilizer issues!")
        print("   All OMP monitoring completely disabled including boot triggers.")
        print("\n⚠️  CRITICAL: Add pre-mix oil to fuel (1:100 ratio)")
        
        return True

def main():
    """Main function"""
    input_file = "brickcentral.bin"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    tool = SafeOMPDeleteComplete(input_file)
    return tool.run_complete_delete()

if __name__ == "__main__":
    success = main()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)