#!/usr/bin/env python3
"""
Minimal Test Tool - ONE MODIFICATION AT A TIME
Test each OMP modification individually to isolate the problem.
"""

import os
import shutil
from datetime import datetime

class MinimalTestTool:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.data = None
        
    def load_firmware(self) -> bool:
        """Load firmware"""
        if not os.path.exists(self.input_file):
            print(f"❌ Error: {self.input_file} not found")
            return False
        
        try:
            with open(self.input_file, 'rb') as f:
                self.data = bytearray(f.read())
            print(f"✅ Loaded: {len(self.data)} bytes")
            return True
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False
    
    def create_single_modification(self, mod_index: int) -> bool:
        """Create firmware with just ONE modification"""
        modifications = [
            {
                'name': 'omp_pressure',
                'location': 0x452b,
                'original': bytes([0x19, 0x00, 0x0b, 0x62]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP pressure monitoring bypass'
            },
            {
                'name': 'omp_flow',
                'location': 0x57ef,
                'original': bytes([0x19, 0x00, 0x09, 0x60]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP flow monitoring bypass'
            },
            {
                'name': 'omp_dtc',
                'location': 0x1d39d,
                'original': bytes([0x19, 0x01, 0xfc, 0x21]),
                'modified': bytes([0x00, 0x09, 0x00, 0x09]),
                'description': 'OMP DTC setting disable'
            },
            {
                'name': 'limp_trigger1',
                'location': 0x9aa,
                'original': bytes([0x20, 0x00]),
                'modified': bytes([0x00, 0x09]),
                'description': 'Limp mode trigger 1 disable'
            },
            {
                'name': 'limp_trigger2',
                'location': 0x134e,
                'original': bytes([0x20, 0x00]),
                'modified': bytes([0x00, 0x09]),
                'description': 'Limp mode trigger 2 disable'
            }
        ]
        
        if mod_index >= len(modifications):
            print(f"❌ Invalid modification index: {mod_index}")
            return False
        
        mod = modifications[mod_index]
        
        # Create backup
        backup_file = f"{self.input_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.input_file, backup_file)
        
        # Create output filename
        output_file = f"test_{mod['name']}.bin"
        
        print(f"\n🔧 Creating test firmware: {output_file}")
        print(f"   Modification: {mod['description']}")
        print(f"   Location: 0x{mod['location']:04X}")
        
        # Check current bytes
        location = mod['location']
        original = mod['original']
        modified = mod['modified']
        
        if location + len(original) > len(self.data):
            print(f"❌ ERROR: Location beyond file bounds")
            return False
        
        current = self.data[location:location + len(original)]
        
        print(f"   Current:  {' '.join(f'{b:02x}' for b in current)}")
        print(f"   Expected: {' '.join(f'{b:02x}' for b in original)}")
        print(f"   Modified: {' '.join(f'{b:02x}' for b in modified)}")
        
        if current != original:
            print(f"⚠️  WARNING: Current bytes don't match expected")
            print(f"   Applying anyway for testing...")
        
        # Apply single modification
        self.data[location:location + len(modified)] = modified
        
        # Save test firmware
        try:
            with open(output_file, 'wb') as f:
                f.write(self.data)
            print(f"✅ Created: {output_file}")
            
            # Create report
            report_file = f"test_{mod['name']}_REPORT.txt"
            with open(report_file, 'w') as f:
                f.write(f"MINIMAL TEST - SINGLE MODIFICATION\n")
                f.write(f"==================================\n\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Test: {mod['name']}\n")
                f.write(f"Description: {mod['description']}\n")
                f.write(f"Location: 0x{mod['location']:04X}\n")
                f.write(f"Original: {' '.join(f'{b:02x}' for b in original)}\n")
                f.write(f"Modified: {' '.join(f'{b:02x}' for b in modified)}\n\n")
                f.write(f"Output: {output_file}\n")
                f.write(f"Backup: {backup_file}\n\n")
                f.write(f"TEST PURPOSE:\n")
                f.write(f"Flash this file and test if ECU starts without relay of death.\n")
                f.write(f"If this single modification causes issues, we know this\n")
                f.write(f"specific location/modification is problematic.\n")
            
            print(f"✅ Report: {report_file}")
            return True
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def create_alternative_nop_test(self) -> bool:
        """Test different NOP instruction patterns"""
        print(f"\n🔬 Creating alternative NOP instruction tests...")
        
        # Different possible NOP patterns for Renesas/H8 architecture
        nop_patterns = [
            {'name': 'nop_00_00', 'pattern': bytes([0x00, 0x00]), 'desc': 'Standard NOP (0x00 0x00)'},
            {'name': 'nop_09_00', 'pattern': bytes([0x09, 0x00]), 'desc': 'Alternative NOP (0x09 0x00)'},
            {'name': 'nop_01_40', 'pattern': bytes([0x01, 0x40]), 'desc': 'H8 NOP variant (0x01 0x40)'},
            {'name': 'return_now', 'pattern': bytes([0x54, 0x70]), 'desc': 'RTS (return) instruction'},
        ]
        
        # Test location 0x9aa (limp mode trigger 1) with different NOPs
        test_location = 0x9aa
        original_bytes = bytes([0x20, 0x00])
        
        for nop in nop_patterns:
            # Reset data
            if not self.load_firmware():
                continue
                
            output_file = f"test_{nop['name']}.bin"
            
            print(f"\n   Testing: {nop['desc']}")
            print(f"   Location: 0x{test_location:04X}")
            print(f"   Pattern: {' '.join(f'{b:02x}' for b in nop['pattern'])}")
            
            # Apply modification
            self.data[test_location:test_location + len(nop['pattern'])] = nop['pattern']
            
            # Save
            try:
                with open(output_file, 'wb') as f:
                    f.write(self.data)
                print(f"   ✅ Created: {output_file}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
    
    def run_minimal_tests(self) -> bool:
        """Run all minimal tests"""
        print("🔬 MINIMAL TEST TOOL")
        print("=" * 25)
        print("Creates individual test files for each modification")
        print("Test each file separately to isolate the problem\n")
        
        if not self.load_firmware():
            return False
        
        print("Creating individual modification tests...")
        
        # Create test for each individual modification
        for i in range(5):
            # Reload original data for each test
            if not self.load_firmware():
                continue
            
            print(f"\n--- Test {i+1}/5 ---")
            self.create_single_modification(i)
        
        # Create alternative NOP tests
        self.create_alternative_nop_test()
        
        print("\n" + "=" * 60)
        print("✅ MINIMAL TESTS CREATED")
        print("=" * 60)
        print("\nTest files created:")
        print("1. test_omp_pressure.bin     - OMP pressure monitoring only")
        print("2. test_omp_flow.bin         - OMP flow monitoring only") 
        print("3. test_omp_dtc.bin          - OMP DTC setting only")
        print("4. test_limp_trigger1.bin    - Limp mode trigger 1 only")
        print("5. test_limp_trigger2.bin    - Limp mode trigger 2 only")
        print("\nAlternative NOP tests:")
        print("6. test_nop_00_00.bin        - Standard NOP (0x00 0x00)")
        print("7. test_nop_09_00.bin        - Alternative NOP (0x09 0x00)")
        print("8. test_nop_01_40.bin        - H8 NOP variant")
        print("9. test_return_now.bin       - RTS instruction")
        
        print("\n🎯 TESTING STRATEGY:")
        print("1. Flash test_omp_pressure.bin first (safest)")
        print("2. If it works, try test_omp_flow.bin")
        print("3. Continue until you find the problematic modification")
        print("4. If OMP modifications work, try limp mode triggers")
        print("5. If all fail, try alternative NOP patterns")
        
        print("\n⚠️  If test_omp_pressure.bin causes relay of death:")
        print("   - Our modification locations are wrong")
        print("   - Need to research actual working examples")
        
        return True

def main():
    """Main function"""
    input_file = "brickcentral.bin"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return False
    
    tool = MinimalTestTool(input_file)
    return tool.run_minimal_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)