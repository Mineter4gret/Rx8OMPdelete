#!/usr/bin/env python3
"""
Mazda RX8 N3H6 ECU OMP Delete Tool
This tool modifies the ECU binary to remove OMP monitoring and prevent limp mode.

WARNING: This tool modifies critical engine management systems.
Use at your own risk. Engine damage may occur without proper lubrication.
"""

import os
import shutil
import struct
import hashlib
from datetime import datetime

class OMPDeleteTool:
    def __init__(self, input_file):
        self.input_file = input_file
        self.backup_file = f"{input_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_file = f"{input_file.replace('.bin', '_omp_deleted.bin')}"
        self.data = None
        
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
    
    def backup_original(self):
        """Create a backup of the original binary"""
        print(f"Creating backup: {self.backup_file}")
        try:
            shutil.copy2(self.input_file, self.backup_file)
            print("Backup created successfully")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def calculate_checksum(self):
        """Calculate MD5 checksum of the current data"""
        return hashlib.md5(self.data).hexdigest()
    
    def apply_omp_modifications(self):
        """Apply OMP delete modifications"""
        print("\n=== Applying OMP Delete Modifications ===")
        
        # Store original checksum
        original_checksum = self.calculate_checksum()
        print(f"Original checksum: {original_checksum}")
        
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
            }
        ]
        
        applied_modifications = 0
        
        for mod in modifications:
            location = mod['location']
            original = mod['original']
            modified = mod['modified']
            description = mod['description']
            
            print(f"\nChecking location 0x{location:04x}: {description}")
            
            # Check if we're within file bounds
            if location + len(original) > len(self.data):
                print(f"  ERROR: Location extends beyond file size")
                continue
                
            # Check if original bytes match
            current_bytes = self.data[location:location + len(original)]
            if current_bytes == original:
                print(f"  Original bytes match: {' '.join(f'{b:02x}' for b in original)}")
                print(f"  Applying modification: {' '.join(f'{b:02x}' for b in modified)}")
                
                # Apply modification
                self.data[location:location + len(modified)] = modified
                applied_modifications += 1
                print(f"  ✓ Modification applied successfully")
            else:
                print(f"  WARNING: Original bytes don't match")
                print(f"  Expected: {' '.join(f'{b:02x}' for b in original)}")
                print(f"  Found:    {' '.join(f'{b:02x}' for b in current_bytes)}")
                print(f"  Skipping this modification")
        
        # Calculate new checksum
        new_checksum = self.calculate_checksum()
        print(f"\nModifications applied: {applied_modifications}/{len(modifications)}")
        print(f"New checksum: {new_checksum}")
        
        return applied_modifications > 0
    
    def additional_safety_modifications(self):
        """Apply additional safety modifications to prevent limp mode"""
        print("\n=== Applying Additional Safety Modifications ===")
        
        # Look for additional limp mode triggers
        limp_patterns = [
            (0x9aa, bytes([0x20, 0x00]), bytes([0x00, 0x09])),
            (0x134e, bytes([0x20, 0x00]), bytes([0x00, 0x09])),
        ]
        
        applied = 0
        for location, original, modified in limp_patterns:
            if location + len(original) <= len(self.data):
                current = self.data[location:location + len(original)]
                if current == original:
                    print(f"  Modifying limp mode trigger at 0x{location:04x}")
                    self.data[location:location + len(modified)] = modified
                    applied += 1
        
        print(f"Additional safety modifications applied: {applied}")
        return applied > 0
    
    def verify_modifications(self):
        """Verify that modifications were applied correctly"""
        print("\n=== Verifying Modifications ===")
        
        # Check key locations
        checks = [
            (0x452b, bytes([0x00, 0x09, 0x00, 0x09]), "OMP pressure bypass"),
            (0x57ef, bytes([0x00, 0x09, 0x00, 0x09]), "OMP flow bypass"),
            (0x1d39d, bytes([0x00, 0x09, 0x00, 0x09]), "DTC disable"),
        ]
        
        all_verified = True
        for location, expected, description in checks:
            current = self.data[location:location + len(expected)]
            if current == expected:
                print(f"  ✓ {description} verified at 0x{location:04x}")
            else:
                print(f"  ✗ {description} verification failed at 0x{location:04x}")
                all_verified = False
        
        return all_verified
    
    def save_modified_binary(self):
        """Save the modified binary to output file"""
        print(f"\nSaving modified binary: {self.output_file}")
        try:
            with open(self.output_file, 'wb') as f:
                f.write(self.data)
            print("Modified binary saved successfully")
            
            # Verify file size
            file_size = os.path.getsize(self.output_file)
            print(f"Output file size: {file_size} bytes")
            
            return True
        except Exception as e:
            print(f"Error saving modified binary: {e}")
            return False
    
    def generate_report(self):
        """Generate a modification report"""
        report_file = f"{self.output_file.replace('.bin', '_report.txt')}"
        
        print(f"\nGenerating report: {report_file}")
        
        try:
            with open(report_file, 'w') as f:
                f.write("=== Mazda RX8 N3H6 ECU OMP Delete Report ===\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"Output file: {self.output_file}\n")
                f.write(f"Backup file: {self.backup_file}\n\n")
                
                f.write("Modifications Applied:\n")
                f.write("1. OMP pressure monitoring bypass (0x452b)\n")
                f.write("2. OMP flow monitoring bypass (0x57ef)\n")
                f.write("3. OMP DTC setting disable (0x1d39d)\n\n")
                
                f.write("IMPORTANT SAFETY WARNINGS:\n")
                f.write("- Pre-mix oil MUST be added to fuel (1:100 ratio recommended)\n")
                f.write("- Monitor engine temperatures closely\n")
                f.write("- Test thoroughly before daily driving\n")
                f.write("- This modification may void warranty\n")
                f.write("- Engine damage may occur without proper lubrication\n\n")
                
                f.write("Post-Modification Checklist:\n")
                f.write("[ ] ECU programmed successfully\n")
                f.write("[ ] Engine starts and idles\n")
                f.write("[ ] No immediate error codes\n")
                f.write("[ ] Pre-mix oil system implemented\n")
                f.write("[ ] Performance testing completed\n")
                
            print("Report generated successfully")
            return True
        except Exception as e:
            print(f"Error generating report: {e}")
            return False
    
    def run(self):
        """Run the complete OMP delete process"""
        print("=== Mazda RX8 N3H6 ECU OMP Delete Tool ===")
        print("WARNING: This tool modifies critical engine management systems!")
        print("Use at your own risk. Ensure proper lubrication with pre-mix oil.\n")
        
        # Load binary
        if not self.load_binary():
            return False
        
        # Create backup
        if not self.backup_original():
            return False
        
        # Apply modifications
        if not self.apply_omp_modifications():
            print("Failed to apply OMP modifications")
            return False
        
        # Apply additional safety modifications
        self.additional_safety_modifications()
        
        # Verify modifications
        if not self.verify_modifications():
            print("Modification verification failed")
            return False
        
        # Save modified binary
        if not self.save_modified_binary():
            return False
        
        # Generate report
        self.generate_report()
        
        print("\n=== OMP Delete Process Complete ===")
        print(f"Modified binary saved as: {self.output_file}")
        print(f"Original binary backed up as: {self.backup_file}")
        print("\nIMPORTANT: Remember to add pre-mix oil to your fuel!")
        print("Recommended ratio: 1:100 (2-stroke oil:fuel)")
        
        return True

def main():
    """Main function"""
    input_file = "brickcentral.bin"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    tool = OMPDeleteTool(input_file)
    return tool.run()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)