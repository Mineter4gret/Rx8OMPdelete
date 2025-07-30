#!/usr/bin/env python3
"""
Simple OMP Delete Tool - NO CHECKSUM HANDLING
Only applies modifications - let the flashing program handle checksums.
"""

import os
import shutil
from datetime import datetime

class SimpleOMPDelete:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.backup_file = f"{input_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_file = f"{input_file.replace('.bin', '_omp_deleted_simple.bin')}"
        self.data = None
        self.applied_modifications = []
        
    def load_and_backup(self) -> bool:
        """Load firmware and create backup"""
        print("📂 Loading firmware and creating backup...")
        
        if not os.path.exists(self.input_file):
            print(f"❌ Error: {self.input_file} not found")
            return False
        
        # Load firmware
        try:
            with open(self.input_file, 'rb') as f:
                self.data = bytearray(f.read())
            print(f"✅ Loaded: {len(self.data)} bytes")
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False
        
        # Create backup
        try:
            shutil.copy2(self.input_file, self.backup_file)
            print(f"✅ Backup: {self.backup_file}")
            return True
        except Exception as e:
            print(f"❌ Backup error: {e}")
            return False
    
    def apply_omp_modifications_only(self) -> bool:
        """Apply ONLY the OMP modifications - no checksum handling"""
        print("\n🔧 Applying OMP delete modifications...")
        print("   (Checksums will be handled by flashing program)")
        
        # All OMP modifications
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
                'description': 'Limp mode trigger 1 disable'
            },
            {
                'location': 0x134e,
                'original': bytes([0x20, 0x00]),
                'modified': bytes([0x00, 0x09]),
                'description': 'Limp mode trigger 2 disable'
            }
        ]
        
        print(f"\nApplying {len(modifications)} modifications:")
        
        for mod in modifications:
            location = mod['location']
            original = mod['original']
            modified = mod['modified']
            description = mod['description']
            
            print(f"\n  {description}")
            print(f"    Location: 0x{location:04X}")
            
            # Bounds check
            if location + len(original) > len(self.data):
                print(f"    ❌ ERROR: Beyond file bounds")
                continue
            
            # Get current bytes
            current = self.data[location:location + len(original)]
            
            print(f"    Current:  {' '.join(f'{b:02x}' for b in current)}")
            print(f"    Expected: {' '.join(f'{b:02x}' for b in original)}")
            print(f"    Modified: {' '.join(f'{b:02x}' for b in modified)}")
            
            if current == original:
                # Apply modification
                self.data[location:location + len(modified)] = modified
                self.applied_modifications.append(mod)
                print(f"    ✅ Applied successfully")
                
            elif current == modified:
                self.applied_modifications.append(mod)
                print(f"    ℹ️  Already applied")
                
            else:
                print(f"    ⚠️  Unexpected bytes - applying anyway")
                self.data[location:location + len(modified)] = modified
                self.applied_modifications.append(mod)
                print(f"    🔧 Forced application")
        
        print(f"\n📊 Total applied: {len(self.applied_modifications)}/{len(modifications)}")
        return len(self.applied_modifications) > 0
    
    def save_modified_firmware(self) -> bool:
        """Save the modified firmware (no checksum changes)"""
        print(f"\n💾 Saving modified firmware: {self.output_file}")
        print("   NOTE: Checksums unchanged - flashing program will handle them")
        
        try:
            with open(self.output_file, 'wb') as f:
                f.write(self.data)
            
            size = os.path.getsize(self.output_file)
            print(f"✅ Saved: {size} bytes")
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def generate_simple_report(self) -> bool:
        """Generate simple report"""
        report_file = f"{self.output_file.replace('.bin', '_REPORT.txt')}"
        
        try:
            with open(report_file, 'w') as f:
                f.write("SIMPLE OMP DELETE TOOL - NO CHECKSUM HANDLING\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Input: {self.input_file}\n")
                f.write(f"Output: {self.output_file}\n")
                f.write(f"Backup: {self.backup_file}\n\n")
                
                f.write("MODIFICATIONS APPLIED:\n")
                for mod in self.applied_modifications:
                    f.write(f"- {mod['description']} at 0x{mod['location']:04X}\n")
                    f.write(f"  Original: {' '.join(f'{b:02x}' for b in mod['original'])}\n")
                    f.write(f"  Modified: {' '.join(f'{b:02x}' for b in mod['modified'])}\n\n")
                
                f.write("IMPORTANT NOTES:\n")
                f.write("- NO checksum modifications made\n")
                f.write("- Flashing program will calculate checksums automatically\n")
                f.write("- Pre-mix oil REQUIRED (1:100 ratio)\n")
                f.write("- Monitor engine parameters after installation\n\n")
                
                f.write("RECOVERY:\n")
                f.write(f"If issues occur, restore: {self.backup_file}\n")
            
            print(f"✅ Report: {report_file}")
            return True
        except Exception as e:
            print(f"❌ Report error: {e}")
            return False
    
    def run_simple_delete(self) -> bool:
        """Run simple OMP delete - modifications only"""
        print("🎯 SIMPLE OMP DELETE TOOL")
        print("=" * 30)
        print("Applies modifications only - no checksum handling")
        print("Your flashing program will calculate checksums automatically\n")
        
        if not self.load_and_backup():
            return False
        
        if not self.apply_omp_modifications_only():
            return False
        
        if not self.save_modified_firmware():
            return False
        
        self.generate_simple_report()
        
        print("\n" + "=" * 50)
        print("✅ SIMPLE OMP DELETE COMPLETE")
        print("=" * 50)
        print(f"Modified firmware: {self.output_file}")
        print(f"Original backup: {self.backup_file}")
        print("\n🎯 Ready for flashing!")
        print("   Your flashing program will handle checksums automatically.")
        print("\n⚠️  REMEMBER: Add pre-mix oil to fuel (1:100 ratio)")
        
        return True

def main():
    """Main function"""
    input_file = "brickcentral.bin"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return False
    
    tool = SimpleOMPDelete(input_file)
    return tool.run_simple_delete()

if __name__ == "__main__":
    success = main()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)