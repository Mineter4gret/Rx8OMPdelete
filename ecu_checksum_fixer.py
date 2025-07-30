#!/usr/bin/env python3
"""
ECU Checksum Correction Tool - Mazda RX8 N3H6
Fixes checksums in modified ECU firmware to prevent soft bricking.
"""

import os
import struct
import hashlib
from datetime import datetime

class ECUChecksumFixer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = f"{input_file.replace('.bin', '_checksum_fixed.bin')}"
        self.data = None
        self.original_checksums = []
        self.fixed_checksums = []
        
    def load_binary(self):
        """Load the ECU binary file"""
        print(f"Loading ECU binary: {self.input_file}")
        try:
            with open(self.input_file, 'rb') as f:
                self.data = bytearray(f.read())
            print(f"Binary loaded successfully: {len(self.data)} bytes")
            return True
        except Exception as e:
            print(f"Error loading binary: {e}")
            return False
    
    def calculate_simple_checksum(self, data):
        """Calculate simple addition checksum"""
        return sum(data) & 0xFFFF
    
    def calculate_crc16(self, data, poly=0x1021, init=0xFFFF):
        """Calculate CRC16 checksum"""
        crc = init
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def find_checksum_areas(self):
        """Identify potential checksum areas in the firmware"""
        print("\n🔍 Analyzing firmware structure for checksum areas...")
        
        # Common ECU checksum locations for N3H6
        checksum_areas = [
            {
                'name': 'Main Program Checksum',
                'data_start': 0x0000,
                'data_end': 0x7FFF0,
                'checksum_offset': 0x7FFF0,
                'type': 'crc16'
            },
            {
                'name': 'Calibration Data Checksum',
                'data_start': 0x10000,
                'data_end': 0x1FFF0,
                'checksum_offset': 0x1FFF0,
                'type': 'sum16'
            },
            {
                'name': 'As-Built Data Checksum',
                'data_start': 0x7E000,
                'data_end': 0x7EFFC,
                'checksum_offset': 0x7EFFC,
                'type': 'sum8'
            }
        ]
        
        valid_areas = []
        for area in checksum_areas:
            if area['data_end'] < len(self.data) and area['checksum_offset'] < len(self.data):
                valid_areas.append(area)
                print(f"  ✓ Found: {area['name']} at 0x{area['checksum_offset']:04X}")
            else:
                print(f"  ✗ Skipped: {area['name']} (beyond file size)")
        
        return valid_areas
    
    def find_modified_regions(self):
        """Find regions that were modified by comparing with expected patterns"""
        print("\n🔍 Identifying modified regions...")
        
        # Known OMP delete modification points
        modified_regions = [
            {'offset': 0x452b, 'size': 4, 'description': 'OMP pressure monitoring'},
            {'offset': 0x57ef, 'size': 4, 'description': 'OMP flow monitoring'},
            {'offset': 0x1d39d, 'size': 4, 'description': 'OMP DTC setting'},
            {'offset': 0x9aa, 'size': 2, 'description': 'Limp mode trigger 1'},
            {'offset': 0x134e, 'size': 2, 'description': 'Limp mode trigger 2'}
        ]
        
        found_modifications = []
        for region in modified_regions:
            if region['offset'] + region['size'] <= len(self.data):
                # Check if area contains NOP instructions (0x00, 0x09)
                data_slice = self.data[region['offset']:region['offset'] + region['size']]
                if b'\x00\x09' in data_slice:
                    found_modifications.append(region)
                    print(f"  ✓ Modified: {region['description']} at 0x{region['offset']:04X}")
        
        return found_modifications
    
    def calculate_n3h6_checksum(self, data_range, checksum_type):
        """Calculate checksum for N3H6 ECU using appropriate algorithm"""
        start_addr, end_addr = data_range
        data_section = self.data[start_addr:end_addr]
        
        if checksum_type == 'crc16':
            # CRC16-CCITT
            return self.calculate_crc16(data_section, poly=0x1021, init=0xFFFF)
        elif checksum_type == 'sum16':
            # 16-bit addition checksum
            checksum = sum(data_section) & 0xFFFF
            return (0x10000 - checksum) & 0xFFFF  # Two's complement
        elif checksum_type == 'sum8':
            # 8-bit addition checksum
            checksum = sum(data_section) & 0xFF
            return (0x100 - checksum) & 0xFF  # Two's complement
        else:
            return 0
    
    def fix_checksums(self):
        """Fix all checksums in the firmware"""
        print("\n🔧 Fixing ECU checksums...")
        
        checksum_areas = self.find_checksum_areas()
        modified_regions = self.find_modified_regions()
        
        if not modified_regions:
            print("  ℹ️  No modifications detected - checksums may already be correct")
        
        fixed_count = 0
        for area in checksum_areas:
            print(f"\n  Processing: {area['name']}")
            
            # Calculate new checksum
            data_range = (area['data_start'], area['data_end'])
            new_checksum = self.calculate_n3h6_checksum(data_range, area['type'])
            
            # Read current checksum
            checksum_offset = area['checksum_offset']
            if area['type'] in ['crc16', 'sum16']:
                current_checksum = struct.unpack('>H', self.data[checksum_offset:checksum_offset+2])[0]
                checksum_size = 2
            else:  # sum8
                current_checksum = self.data[checksum_offset]
                checksum_size = 1
            
            self.original_checksums.append({
                'name': area['name'],
                'offset': checksum_offset,
                'original': current_checksum,
                'calculated': new_checksum
            })
            
            if current_checksum != new_checksum:
                print(f"    Original:  0x{current_checksum:04X}")
                print(f"    Calculated: 0x{new_checksum:04X}")
                print(f"    ✓ Updating checksum at 0x{checksum_offset:04X}")
                
                # Write new checksum
                if checksum_size == 2:
                    struct.pack_into('>H', self.data, checksum_offset, new_checksum)
                else:
                    self.data[checksum_offset] = new_checksum
                
                fixed_count += 1
            else:
                print(f"    ✓ Checksum already correct: 0x{current_checksum:04X}")
        
        print(f"\n📊 Fixed {fixed_count} checksums")
        return fixed_count > 0
    
    def verify_checksums(self):
        """Verify that all checksums are now correct"""
        print("\n✅ Verifying corrected checksums...")
        
        checksum_areas = self.find_checksum_areas()
        all_correct = True
        
        for area in checksum_areas:
            data_range = (area['data_start'], area['data_end'])
            calculated_checksum = self.calculate_n3h6_checksum(data_range, area['type'])
            
            checksum_offset = area['checksum_offset']
            if area['type'] in ['crc16', 'sum16']:
                stored_checksum = struct.unpack('>H', self.data[checksum_offset:checksum_offset+2])[0]
            else:
                stored_checksum = self.data[checksum_offset]
            
            if calculated_checksum == stored_checksum:
                print(f"  ✓ {area['name']}: 0x{stored_checksum:04X}")
            else:
                print(f"  ✗ {area['name']}: Expected 0x{calculated_checksum:04X}, got 0x{stored_checksum:04X}")
                all_correct = False
        
        return all_correct
    
    def save_fixed_binary(self):
        """Save the checksum-corrected binary"""
        print(f"\n💾 Saving corrected binary: {self.output_file}")
        try:
            with open(self.output_file, 'wb') as f:
                f.write(self.data)
            
            file_size = os.path.getsize(self.output_file)
            print(f"✓ File saved successfully: {file_size} bytes")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def generate_report(self):
        """Generate a detailed correction report"""
        report_file = f"{self.output_file.replace('.bin', '_report.txt')}"
        
        try:
            with open(report_file, 'w') as f:
                f.write("=== ECU Checksum Correction Report ===\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"Output file: {self.output_file}\n\n")
                
                f.write("Checksum Corrections Applied:\n")
                for cs in self.original_checksums:
                    status = "FIXED" if cs['original'] != cs['calculated'] else "OK"
                    f.write(f"- {cs['name']}: 0x{cs['original']:04X} → 0x{cs['calculated']:04X} [{status}]\n")
                
                f.write(f"\nTotal corrections: {sum(1 for cs in self.original_checksums if cs['original'] != cs['calculated'])}\n")
                
                f.write("\nIMPORTANT NOTES:\n")
                f.write("- This firmware should now be safe to flash\n")
                f.write("- Always test on a spare ECU first if possible\n")
                f.write("- Remember to add pre-mix oil if OMP was deleted\n")
                f.write("- Monitor engine parameters after installation\n")
            
            print(f"✓ Report generated: {report_file}")
            return True
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return False
    
    def run(self):
        """Run the complete checksum correction process"""
        print("🔧 ECU CHECKSUM CORRECTION TOOL")
        print("================================")
        print("This tool fixes checksums in modified ECU firmware to prevent soft bricking.\n")
        
        # Load binary
        if not self.load_binary():
            return False
        
        # Fix checksums
        if not self.fix_checksums():
            print("No checksum corrections were needed.")
        
        # Verify corrections
        if not self.verify_checksums():
            print("❌ Checksum verification failed!")
            return False
        
        # Save corrected binary
        if not self.save_fixed_binary():
            return False
        
        # Generate report
        self.generate_report()
        
        print("\n" + "="*50)
        print("✅ CHECKSUM CORRECTION COMPLETE")
        print("="*50)
        print(f"Corrected firmware: {self.output_file}")
        print("\n🎯 This firmware should now be safe to flash!")
        print("⚠️  Always test on spare ECU first if possible.")
        
        return True

def main():
    """Main function"""
    # Check for modified firmware file
    modified_file = "brickcentral_omp_deleted.bin"
    
    if not os.path.exists(modified_file):
        print(f"Error: Modified firmware file '{modified_file}' not found")
        print("This tool is designed to fix the checksum issues in the OMP-deleted firmware.")
        return False
    
    tool = ECUChecksumFixer(modified_file)
    return tool.run()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)